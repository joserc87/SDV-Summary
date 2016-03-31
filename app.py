#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, redirect, url_for, request, flash, g, jsonify, make_response
import time
from werkzeug import secure_filename, check_password_hash
import os
from playerInfo import playerInfo
from farmInfo import getFarmInfo
from bigbase import dec2big
import json
import hashlib
from imageDrone import process_queue
from createdb import database_structure_dict, database_fields
import defusedxml
import operator
import random
import sqlite3
import psycopg2
import io
from xml.etree.ElementTree import ParseError
import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']
if app.config['USE_SQLITE'] == True:
	app.database = app.config['DB_SQLITE']
	app.sqlesc = '?'
	def connect_db():
		return sqlite3.connect(app.database)
else:
	app.database = 'dbname='+app.config['DB_NAME']+' user='+app.config['DB_USER']+' password='+app.config['DB_PASSWORD']
	app.sqlesc = '%s'
	def connect_db():
		return psycopg2.connect(app.database)

def md5(md5file):
	h = hashlib.md5()
	if type(md5file) == io.BytesIO:
		h.update(md5file.getvalue())
	else:
		for chunk in iter(lambda: md5file.read(4096), b""):
			h.update(chunk)
	return h.hexdigest()

@app.route('/_get_recents')
def jsonifyRecents():
	return jsonify(recents=get_recents()['posts'])

@app.route('/',methods=['GET','POST'])
def home():
	start_time = time.time()
	error = None
	if request.method == 'POST':
		inputfile = request.files['file']
		if inputfile:
			memfile = io.BytesIO()
			inputfile.save(memfile)
			md5_info = md5(memfile)
			try:
				player_info = playerInfo(memfile.getvalue(),True)
			except defusedxml.common.EntitiesForbidden:
				error = "I don't think that's very funny"
				return render_template("index.html", error=error,blogposts=get_blogposts(5), recents=get_recents(), processtime=round(time.time()-start_time,5))
			except IOError:
				error = "Savegame failed sanity check (if you think this is in error please let us know)"
				g.db = connect_db()
				cur = g.db.cursor()
				cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'],time.time(),'failed sanity check '+str(filename)))
				g.db.commit()
				g.db.close()
				return render_template("index.html", error=error,blogposts=get_blogposts(5), recents=get_recents(), processtime=round(time.time()-start_time,5))
			except AttributeError as e:
				error = "Not valid save file - did you select file 'SaveGameInfo' instead of 'playername_number'?"
				return render_template("index.html", error=error,blogposts=get_blogposts(5), recents=get_recents(), processtime=round(time.time()-start_time,5))
			except ParseError as e:
				error = "Not well-formed xml"
				return render_template("index.html",error=error,blogposts=get_blogposts(5),recents=get_recents(), processtime=round(time.time()-start_time,5))
			g.db = connect_db()
			cur = g.db.cursor()
			dupe = is_duplicate(md5_info,player_info)
			if dupe != False:
				session[dupe] = md5_info
				return redirect(url_for('display_data',url=dupe))
			else:
				farm_info = getFarmInfo(memfile.getvalue(),True)
				outcome, error = insert_info(player_info,farm_info,md5_info)
				if outcome != False:
					filename = os.path.join(app.config['UPLOAD_FOLDER'],outcome)
					with open(filename,'wb') as f:
						f.write(memfile.getvalue())
					cur.execute('UPDATE playerinfo SET savefileLocation='+app.sqlesc+' WHERE url='+app.sqlesc+'',(filename,outcome))
					g.db.commit()
				process_queue()
			memfile.close()
			g.db.close()
			if outcome != False:
				session[outcome] = md5_info
				return redirect(url_for('display_data',url=outcome))
	return render_template("index.html", recents=get_recents(), error=error,blogposts=get_blogposts(5), processtime=round(time.time()-start_time,5))

def get_recents(n=6,**kwargs):
	g.db = connect_db()
	cur = g.db.cursor()
	recents = {}
	query = 'SELECT url, name, farmName, date, avatar_url, farm_url FROM playerinfo ORDER BY id DESC LIMIT '+app.sqlesc
	offset = 0
	if 'offset' in kwargs.keys():
		offset = kwargs['offset']
		query += " OFFSET "+app.sqlesc
	if 'offset' in kwargs.keys():
		cur.execute(query,(n,offset))
	else:
		cur.execute(query,(n,))
	recents['posts'] = cur.fetchall()
	cur.execute('SELECT count(*) FROM playerinfo')
	recents['total'] = cur.fetchone()[0]
	if len(recents)==0:
		recents == None
	g.db.close()
	return recents

def is_duplicate(md5_info,player_info):
	cur = g.db.cursor()
	cur.execute('SELECT id, md5, name, uniqueIDForThisGame, url FROM playerinfo WHERE md5='+app.sqlesc+'',(md5_info,))
	matches = cur.fetchall()
	if len(matches) > 0:
		for match in matches:
			if str(player_info['name'])==str(match[2]) and str(player_info['uniqueIDForThisGame'])==str(match[3]):
				return match[4]
		return False
	else:
		return False

def insert_info(player_info,farm_info,md5_info):
	columns = []
	values = []
	# player_info['date'] = ['Spring','Summer','Autumn','Winter'][int(((player_info['stats']['DaysPlayed']%(28*4))-((player_info['stats']['DaysPlayed']%(28*4))%(28)))/28)]+' '+str((player_info['stats']['DaysPlayed']%(28*4))%(28))+', Year '+str(((player_info['stats']['DaysPlayed']-player_info['stats']['DaysPlayed']%(28*4))/(28*4))+1)
	for key in player_info.keys():
		if type(player_info[key]) == list:
			for i,item in enumerate(player_info[key]):
				columns.append(key.replace(' ','_') + str(i))
				values.append(str(item))
		elif type(player_info[key]) == dict:
			for subkey in player_info[key]:
				if type(player_info[key][subkey]) == dict:
					for subsubkey in player_info[key][subkey]:
						columns.append((key+subkey+subsubkey).replace(' ','_'))
						values.append((player_info[key][subkey][subsubkey]))
				else:
					columns.append((key + subkey).replace(' ','_'))
					values.append(str(player_info[key][subkey]))
		else:
			columns.append(key)
			values.append(str(player_info[key]))
	columns.append('farm_info')
	values.append(json.dumps(farm_info))
	columns.append('added_time')
	values.append(time.time())
	columns.append('md5')
	values.append(md5_info)
	columns.append('ip')
	values.append(request.environ['REMOTE_ADDR'])
	columns.append('del_token')
	values.append(random.randint(-(2**63)-1,(2**63)-1))
	columns.append('views')
	values.append('0')

	colstring = ''
	for c in columns:
		colstring += c+', '
	colstring = colstring[:-2]
	questionmarks = ((app.sqlesc+',')*len(values))[:-1]
	try:
		cur = g.db.cursor()
		cur.execute('INSERT INTO playerinfo ('+colstring+') VALUES ('+questionmarks+')',tuple(values))
		cur.execute('SELECT id,added_time FROM playerinfo WHERE uniqueIDForThisGame='+app.sqlesc+' AND name='+app.sqlesc+' AND md5 ='+app.sqlesc+'',(player_info['uniqueIDForThisGame'],player_info['name'],md5_info))
		row = cur.fetchone()
		url = dec2big(int(row[0])+int(row[1]))
		rowid = row[0]
		cur.execute('UPDATE playerinfo SET url='+app.sqlesc+' WHERE id='+app.sqlesc+'',(url,rowid))
		cur.execute('INSERT INTO todo (task, playerid) VALUES ('+app.sqlesc+','+app.sqlesc+')',('process_image',rowid))
		g.db.commit()
		return url, None
	except (sqlite3.OperationalError, psycopg2.ProgrammingError) as e:
		cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'], time.time(),str(e)+' '+str([columns,values])))
		g.db.commit()
		return False, "Save file incompatible with current database: error is "+str(e)

@app.route('/<url>')
def display_data(url):
	error = None
	deletable = None
	start_time = time.time()
	g.db = connect_db()
	cur = g.db.cursor()
	cur.execute('SELECT '+database_fields+' FROM playerinfo WHERE url='+app.sqlesc+'',(url,))
	data = cur.fetchall()
	if len(data) != 1:
		error = 'There is nothing here... is this URL correct?'
		cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'],time.time(),str(len(data))+' cur.fetchall() for url:'+str(url)))
		g.db.commit()
		return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))
	else:
		cur.execute('UPDATE playerinfo SET views=views+1 WHERE url='+app.sqlesc+'',(url,))
		g.db.commit()
		datadict = {}
		for k, key in enumerate(sorted(database_structure_dict.keys())):
			if key != 'farm_info':
				datadict[key] = data[0][k]

		if url in session:
			cur.execute('SELECT url,md5,del_token FROM playerinfo WHERE uniqueIDForThisGame='+app.sqlesc+' AND name='+app.sqlesc+' AND farmName='+app.sqlesc+'',(datadict['uniqueIDForThisGame'],datadict['name'],datadict['farmName']))
			md5_from_db = cur.fetchall()
			if session[url] in [md5[1] for md5 in md5_from_db]:
				deletable = True
				for row in md5_from_db:
					session[row[0]] = row[1]
					session[row[0]+'del_token'] = row[2]

		for item in ['money','totalMoneyEarned','statsStepsTaken','millisecondsPlayed']:
			if item == 'millisecondsPlayed':
				datadict[item] = "{:,}".format(round(float((int(datadict[item])/1000)/3600.0),1))
			else:
				datadict[item] = "{:,}".format(datadict[item])
		
		datadict['animals'] = None if datadict['animals']=='{}' else json.loads(datadict['animals'])
		datadict['portrait_info'] = json.loads(datadict['portrait_info'])
		friendships = sorted([[friendship[11:],datadict[friendship]] for friendship in sorted(database_structure_dict.keys()) if friendship.startswith('friendships') and datadict[friendship]!=None],key=lambda x: x[1])[::-1]
		kills = sorted([[kill[27:].replace('_',' '),datadict[kill]] for kill in sorted(database_structure_dict.keys()) if kill.startswith('statsSpecificMonstersKilled') and datadict[kill]!=None],key=lambda x: x[1])[::-1]
		cur.execute('SELECT url, date FROM playerinfo WHERE uniqueIDForThisGame='+app.sqlesc+' AND name='+app.sqlesc+' AND farmName='+app.sqlesc+' ORDER BY statsDaysPlayed ASC',(datadict['uniqueIDForThisGame'],datadict['name'],datadict['farmName']))
		other_saves = cur.fetchall()
		return render_template("profile.html", deletable=deletable, data=datadict, kills=kills, friendships=friendships, others=other_saves, error=error, processtime=round(time.time()-start_time,5))

@app.route('/<url>/<instruction>')
def operate_on_url(url,instruction):
	error = None
	deletable = None
	start_time = time.time()
	if url in session:
		g.db = connect_db()
		cur = g.db.cursor()
		cur.execute('SELECT id,md5,del_token,url,savefileLocation,avatar_url,farm_url FROM playerinfo WHERE uniqueIDForThisGame=(SELECT uniqueIDForThisGame FROM playerinfo WHERE url='+app.sqlesc+')',(url,))
		data = cur.fetchall()
		if instruction == 'del':
			for row in data:
				if session[url] == row[1] and session[url+'del_token'] == row[2]:
					cur.execute('DELETE FROM playerinfo WHERE id=('+app.sqlesc+')',(row[0],))
					g.db.commit()
					for filename in row[4:7]:
						os.remove(filename)
					session.pop(url,None)
					session.pop(url+'del_token',None)
					return redirect(url_for('home'))
			return render_template("error.html", error="Your session validation data is wrong", processtime=round(time.time()-start_time,5))
		elif instruction == 'delall':
			for row in data:
				if not (session[row[3]] == row[1] and session[url+'del_token']):
					return render_template("error.html", error="Session validation data was wrong for at least one resource", processtime=round(time.time()-start_time,5))
			for row in data:
				cur.execute('DELETE FROM playerinfo WHERE id=('+app.sqlesc+')',(row[0],))
				for filename in row[4:7]:
					os.remove(filename)
				session.pop(row[3],None)
				session.pop(row[3]+'del_token',None)
			g.db.commit()
			return redirect(url_for('home'))
	else:
		return render_template("error.html", error="Unknown instruction or insufficient credentials", processtime=round(time.time()-start_time,5))


@app.route('/admin',methods=['GET','POST'])
def admin_panel():
	start_time = time.time()
	error = None
	if 'admin' in session:
		#trusted
		returned_blog_data = None
		g.db = connect_db()
		cur = g.db.cursor()
		if request.method == 'POST':
			if request.form['blog'] == 'Post':
				live = False
				if 'live' in request.form:
					if request.form['live']=='on':
						live = True
				if request.form['content'] == '' or request.form['blogtitle'] == '':
					error = 'Failed to post blog entry, title or body was empty!'
					returned_blog_data = {'blogtitle':request.form['blogtitle'],
											'content':request.form['content'],
											'checked': live}
				else:
					cur.execute('INSERT INTO blog (time, author, title, post, live) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(int(time.time()),session['admin'],request.form['blogtitle'],request.form['content'],live))
					g.db.commit()
					if live == True:
						flash('Posted blog entry "'+str(request.form['blogtitle']+'"'))
					else:
						flash('Saved unposted blog entry "'+str(request.form['blogtitle']+'"'))	
			elif request.form['blog'] == 'update':
				state = request.form['live'] == 'true'
				cur.execute('UPDATE blog SET live='+app.sqlesc+' WHERE id='+app.sqlesc,(state,request.form['id']))
				g.db.commit()
				return 'Success'
			elif request.form['blog'] == 'delete':
				cur.execute('DELETE FROM blog WHERE id='+app.sqlesc,(request.form['id'],))
				g.db.commit()
				return 'Success'
		cur.execute('SELECT url,name,farmName,date FROM playerinfo')
		entries = cur.fetchall()
		return render_template('adminpanel.html',returned_blog_data=returned_blog_data,blogposts=get_blogposts(include_hidden=True),entries=entries,error=error, processtime=round(time.time()-start_time,5))
	else:
		if request.method == 'POST':
			if 'blog' in request.form:
				return 'Failure'
			try:
				g.db = connect_db()
				cur = g.db.cursor()
				cur.execute('SELECT password FROM admin WHERE username='+app.sqlesc+' ORDER BY id',(request.form['username'],))
				r = cur.fetchone()
				if r != None:
					if check_password_hash(r[0],request.form['password']) == True:
						session['admin']=request.form['username']
						return redirect(url_for('admin_panel'))
					else:
						error = 'Incorrect username or password'	
				else:
					error = 'Incorrect username or password'
			except:
				pass
		return render_template('admin.html',error=error,processtime=round(time.time()-start_time,5))

def get_blogposts(n=False,**kwargs):
	g.db = connect_db()
	cur = g.db.cursor()
	blogposts = None
	query = "SELECT id,time,author,title,post,live FROM blog"
	metaquery = "SELECT count(*) FROM blog"
	try:
		if kwargs['include_hidden'] == False:
			query += " WHERE live='1'"
			metaquery += " WHERE live='1'"
	except KeyError:
		query += " WHERE live='1'"
		metaquery += " WHERE live='1'"
	query += " ORDER BY id DESC"
	if app.config['USE_SQLITE'] == True:
		if n==False:
			n=-1
	if n!=False:
		query += " LIMIT "+app.sqlesc
	offset = 0
	if 'offset' in kwargs.keys():
		offset = kwargs['offset']
	query += " OFFSET "+app.sqlesc
	if n==False:
		cur.execute(query,(offset,))
	else:
		cur.execute(query,(n,offset))
	blogposts = list(cur.fetchall())
	for b,blogentry in enumerate(blogposts):
		blogposts[b] = list(blogentry)
		blogposts[b][1] = datetime.datetime.fromtimestamp(blogentry[1])
	cur.execute(metaquery)
	metadata = cur.fetchone()
	blogdict = {'total':metadata[0],
				'posts':blogposts}
	return blogdict

@app.route('/lo')
def logout():
	if 'admin' in session:
		session.pop('admin',None)
	return redirect(url_for('admin_panel'))

@app.route('/blog')
def blogmain():
	error = None
	start_time = time.time()
	num_entries = 5
	#print request.args.get('p')
	try:
		offset = int(request.args.get('p')) * num_entries
	except:
		offset = 0
	if offset < 0:
		return redirect(url_for('blogmain'))
	blogposts = get_blogposts(num_entries,offset=offset)
	if blogposts['total']<=offset and blogposts['total']>0:
		return redirect(url_for('blogmain'))
	return render_template('blog.html',full=True,offset=offset,blogposts=blogposts,error=error, processtime=round(time.time()-start_time,5))

@app.route('/all')
def allmain():
	error = None
	start_time = time.time()
	num_entries = 18
	#print request.args.get('p')
	try:
		offset = int(request.args.get('p')) * num_entries
	except:
		offset = 0
	if offset < 0:
		return redirect(url_for('allmain'))
	recents = get_recents(num_entries,offset=offset)
	if recents['total']<=offset and recents['total']>0:
		return redirect(url_for('allmain'))
	return render_template('all.html',full=True,offset=offset,recents=recents,error=error, processtime=round(time.time()-start_time,5))


@app.route('/blog/<id>')
def blogindividual(id):
	error = None
	start_time = time.time()
	try:
		blogid = int(id)
		g.db = connect_db()
		cur = g.db.cursor()
		cur.execute("SELECT id,time,author,title,post,live FROM blog WHERE id="+app.sqlesc+" AND live='1'",(blogid,))
		blogdata = cur.fetchone()
		if blogdata != None:
			blogdata = list(blogdata)
			blogdata[1] = datetime.datetime.fromtimestamp(blogdata[1])
			blogposts = {'posts':(blogdata,),'total':1}
			return render_template('blog.html',full=True,offset=0,recents=get_recents(),blogposts=blogposts,error=error, processtime=round(time.time()-start_time,5))
		else:
			error = "No blog with that ID!"
	except:
		error = "No blog with that ID!"
	return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))



@app.route('/dl/<url>')
def retrieve_file(url):
	error=None
	start_time = time.time()
	if 'admin' in session:
		g.db = connect_db()
		cur = g.db.cursor()
		cur.execute('SELECT savefileLocation,name,uniqueIDForThisGame FROM playerinfo WHERE url='+app.sqlesc,(url,))
		result = cur.fetchone()
		if result != None:
			with open(result[0],'rb') as f:
				response = make_response(f.read())
			response.headers["Content-Disposition"] = "attachment; filename="+str(result[1])+'_'+str(result[2])
			return response
		else:
			error = "URL does not exist"
	else:
		error = "Not admin, no download rights!"
	return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))

if __name__ == "__main__":
	app.run(debug=True)