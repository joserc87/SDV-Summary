#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, redirect, url_for, request, flash, g, jsonify, make_response, send_from_directory
import time
from werkzeug import secure_filename, check_password_hash
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.security import generate_password_hash
import os
from playerInfo import playerInfo
from farmInfo import getFarmInfo
from bigbase import dec2big
import generateSavegame
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
from flask_recaptcha import ReCaptcha

app = Flask(__name__)
app.config.from_object(os.environ['SDV_APP_SETTINGS'].strip('"'))
recaptcha = ReCaptcha(app=app)
app.secret_key = app.config['SECRET_KEY']
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.wsgi_app = ProxyFix(app.wsgi_app)
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

@app.route('/login', methods=['GET','POST'])
def login():
	start_time=time.time()
	error=None
	if 'logged_in_user' in session:
		return redirect(url_for('home'))
	if request.method == 'POST':
		if 'email' not in request.form or 'password' not in request.form or request.form['email']=='':
			error = 'Missing email or password for login!'
		else:
			g.db = connect_db()
			cur = g.db.cursor()
			cur.execute('SELECT id,password FROM users WHERE email='+app.sqlesc,(request.form['email'],))
			result = cur.fetchall()
			assert len(result) <= 1
			if len(result) == 0:
				error = 'Username not found!'
			else:
				if check_password_hash(result[0][1],request.form['password']) == True:
					auth_key = dec2big(random.randint(0,(2**128)))
					cur.execute('UPDATE users SET auth_key='+app.sqlesc+', login_time='+app.sqlesc+' WHERE id='+app.sqlesc,(auth_key,time.time(),result[0][0]))
					g.db.commit()
					session['logged_in_user']=(result[0][0],auth_key)
					return redirect(url_for('home'))
				else:
					error = 'Incorrect password!'
	return render_template("login.html",error=error,processtime=round(time.time()-start_time,5))

@app.route('/su',methods=['GET','POST'])
def signup():
	start_time = time.time()
	error=None
	if 'logged_in_user' in session:
		error = 'You are already logged in!'
	elif request.method == 'POST':
		if 'email' not in request.form or 'password' not in request.form or request.form['email']=='':
			error = 'Missing email or password!'
		else:
			if recaptcha.verify():
				g.db = connect_db()
				cur = g.db.cursor()
				cur.execute('SELECT id FROM users WHERE email='+app.sqlesc,(request.form['email'],))
				result = cur.fetchall()
				if len(result) == 0:
					if len(request.form['email'].split('@')) == 2 and len(request.form['email'].split('@')[1].split('.'))> 2:
						cur.execute('INSERT INTO users (email,password) VALUES ('+app.sqlesc+','+app.sqlesc+')',(request.form['email'],generate_password_hash(request.form['password'])))
						g.db.commit()
						flash('You have successfully registered. Now, please sign in!')
						return redirect(url_for('login'))
					else:
						error = 'Invalid email address!'
				else:
					error = 'This email address has already registered'
			else:
				error = 'Captcha failed! If you are human, please try again!'
	return render_template("signup.html",error=error,processtime=round(time.time()-start_time,5))

def logged_in():
	if 'logged_in_user' in session:
		g.db = connect_db()
		cur = g.db.cursor()
		cur.execute('SELECT auth_key FROM users WHERE id='+app.sqlesc,(session['logged_in_user'][0],))
		result = cur.fetchall()
		if result[0][0] == session['logged_in_user'][1]:
			return True
	return False

app.jinja_env.globals.update(logged_in=logged_in)

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
				cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'],time.time(),'failed sanity check '+str(secure_filename(inputfile.filename))))
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
				password_hash = propagate_password(player_info)
				if password_hash == False:
					error = 'Password hash collision!'
					return render_template("error.html",error=error,processtime=round(time.time()-start_time,5))
				elif password_hash != False and password_hash != None:
					player_info['del_password']=password_hash
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

def propagate_password(player_info):
	cur = g.db.cursor()
	cur.execute('SELECT id,del_password FROM playerinfo WHERE uniqueIDForThisGame='+app.sqlesc+' AND name='+app.sqlesc+' AND farmName='+app.sqlesc+'',(player_info['uniqueIDForThisGame'],player_info['name'],player_info['farmName']))
	matches = cur.fetchall()
	password_hash = None
	for match in matches:
		if match[1] != None and password_hash == None:
			password_hash = match[1]
		if match[1] != password_hash:
			return False#means multiple different password hashes in the results... this isn't ideal
	return password_hash

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
		passworded = True if datadict['del_password'] != None else False
		return render_template("profile.html", deletable=deletable, passworded=passworded, data=datadict, kills=kills, friendships=friendships, others=other_saves, error=error, processtime=round(time.time()-start_time,5))

@app.route('/<url>/<instruction>',methods=['GET','POST'])
def operate_on_url(url,instruction):
	error = None
	deletable = None
	start_time = time.time()
	if request.method == 'POST':
		if url in session:
			g.db = connect_db()
			cur = g.db.cursor()
			cur.execute('SELECT id,md5,del_token,url,savefileLocation,avatar_url,farm_url,download_url,del_password,pass_attempts FROM playerinfo WHERE uniqueIDForThisGame=(SELECT uniqueIDForThisGame FROM playerinfo WHERE url='+app.sqlesc+')',(url,))
			data = cur.fetchall()

			if instruction == 'del':
				for row in data:
					if session[url] == row[1] and session[url+'del_token'] == row[2]:
						if row[8] != None:
							if row[9] != None:
								previous = [item for item in json.loads(row[9]) if item > time.time()-(24*3600)]
								if len(previous) >= app.config['PASSWORD_ATTEMPTS_LIMIT']:
									return render_template("error.html", error="Too many bad password attempts, try again later", processtime=round(time.time()-start_time,5))
							else:
								previous = []
							if check_password_hash(row[8],request.form['password']) == False:
								previous.append(time.time())
								cur.execute('UPDATE playerinfo SET pass_attempts='+app.sqlesc+' WHERE id='+app.sqlesc,(json.dumps(previous),row[0]))
								g.db.commit()
								return render_template("error.html", error="Incorrect password", processtime=round(time.time()-start_time,5))		
						cur.execute('DELETE FROM playerinfo WHERE id=('+app.sqlesc+')',(row[0],))
						g.db.commit()
						for filename in row[4:8]:
							if filename != None:
								os.remove(filename)
						session.pop(url,None)
						session.pop(url+'del_token',None)
						return redirect(url_for('home'))
				return render_template("error.html", error="Your session validation data is wrong", processtime=round(time.time()-start_time,5))

			elif instruction == 'delall':
				for row in data:
					if not (session[row[3]] == row[1] and session[url+'del_token']):
						return render_template("error.html", error="Session validation data was wrong for at least one resource", processtime=round(time.time()-start_time,5))
				authstate = []
				for row in data:
					if row[8] != None:
						if row[9] != None:
							previous = [item for item in json.loads(row[9]) if item > time.time()-(24*3600)]
							if len(previous) >= app.config['PASSWORD_ATTEMPTS_LIMIT']:
								authstate.append(408)
						else:
							previous = []
						if check_password_hash(row[8],request.form['password']) == False:
							previous.append(time.time())
							cur.execute('UPDATE playerinfo SET pass_attempts='+app.sqlesc+' WHERE id='+app.sqlesc,(json.dumps(previous),row[0]))
							g.db.commit()
							authstate.append(400)
				if any([i==408 for i in authstate]):
					return render_template("error.html", error="Too many bad password attempts, try again later", processtime=round(time.time()-start_time,5))
				elif any([i==400 for i in authstate]):
					return render_template("error.html", error="Password was incorrect for at least one resource", processtime=round(time.time()-start_time,5))		
				else:
					for row in data:
						cur.execute('DELETE FROM playerinfo WHERE id=('+app.sqlesc+')',(row[0],))
						for filename in row[4:8]:
							if filename != None:
								os.remove(filename)
						session.pop(row[3],None)
						session.pop(row[3]+'del_token',None)
					g.db.commit()
					return redirect(url_for('home'))

			elif instruction == 'pw':
				for row in data:
					if not (session[row[3]] == row[1] and session[url+'del_token'] and row[8] == None):
						return render_template("error.html", error="Session validation data was wrong for at least one resource, or a password was already set", processtime=round(time.time()-start_time,5))
				if len(request.form['password']) < app.config['PASSWORD_MIN_LENGTH']:
					return render_template("error.html", error="Password too short, minimum length is "+str(app.config['PASSWORD_MIN_LENGTH']), processtime=round(time.time()-start_time,5))
				password_hash = generate_password_hash(request.form['password'])
				for row in data:
					cur.execute('UPDATE playerinfo SET del_password='+app.sqlesc+' WHERE id='+app.sqlesc,(password_hash,row[0]))
				g.db.commit()
				return redirect(url_for('display_data',url=url))
		else:
			return render_template("error.html", error="Unknown instruction or insufficient credentials", processtime=round(time.time()-start_time,5))
	else:
		return redirect(url_for('display_data',url=url))

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
			else:
				try:
					g.db = connect_db()
					cur = g.db.cursor()
					cur.execute('SELECT password FROM admin WHERE username='+app.sqlesc+' ORDER BY id',(request.form['username'],))
					r = cur.fetchone()
					if r != None:
						if check_password_hash(r[0],request.form['password']) == True:
							session['admin']=request.form['username']
							return redirect(url_for('admin_panel'))
					cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'], time.time(),'failed login: '+request.form['username']))
					g.db.commit()
					g.db.close()
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
	session.pop('logged_in_user',None)
	return redirect(url_for('home'))

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
	except TypeError:
		offset = 0
	except:
		error = "No browse with that ID!"
		return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))
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
	g.db = connect_db()
	cur = g.db.cursor()
	cur.execute("SELECT savefileLocation,name,uniqueIDForThisGame,del_password,download_url,id FROM playerinfo WHERE url="+app.sqlesc,(url,))
	result = cur.fetchone()
	if result[3] != None:
		if result[4] == None:
			filename = generateSavegame.createZip(url,result[1],result[2],'static/saves',result[0])
			cur.execute('UPDATE playerinfo SET download_url='+app.sqlesc+' WHERE id='+app.sqlesc,(filename,result[5]))
			g.db.commit()
			return redirect(filename)
		else:
			return redirect(result[4])
	elif 'admin' in session:
		if result != None:
			with open(result[0],'rb') as f:
				response = make_response(f.read())
			response.headers["Content-Disposition"] = "attachment; filename="+str(result[1])+'_'+str(result[2])
			return response
		else:
			error = "URL does not exist"
	else:
		error = "You are unable to download this farm data at this time."
	return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))

@app.route('/faq')
def faq():
	error = None
	start_time=time.time()
	return render_template('faq.html',error=error,processtime=round(time.time()-start_time,5))

if __name__ == "__main__":
	app.run()