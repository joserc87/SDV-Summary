#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, redirect, url_for, request, flash, g
import time
import config
from werkzeug import secure_filename
import os
from playerInfo import playerInfo
from farmInfo import getFarmInfo
import sqlite3
from bigbase import dec2big
import json
import hashlib
from imageDrone import process_queue
from createdb import database_structure_dict, database_fields
import defusedxml
import operator
import random

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
app.database = config.db

def md5(filename):
	h = hashlib.md5()
	with open(filename, 'rb') as f:
		for chunk in iter(lambda: f.read(4096), b""):
			h.update(chunk)
	return h.hexdigest()

@app.route('/',methods=['GET','POST'])
def home():
	start_time = time.time()
	error = None
	if request.method == 'POST':
		inputfile = request.files['file']
		if inputfile:
			filename = secure_filename(inputfile.filename)
			inputfile.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			md5_info = md5(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			try:
				player_info = playerInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			except defusedxml.common.EntitiesForbidden:
				error = "I don't think that's very funny"
				return render_template("index.html", error=error, recents=get_recents(), processtime=round(time.time()-start_time,5))
			except IOError:
				error = "Savegame failed sanity check (if you think this is in error please let us know)"
				g.db = connect_db()
				g.db.execute('INSERT INTO errors (ip, time, notes) VALUES (?,?,?)',(request.environ['REMOTE_ADDR'],time.time(),'failed sanity check '+str(filename)))
				g.db.commit()
				g.db.close()
				return render_template("index.html", error=error, recents=get_recents(), processtime=round(time.time()-start_time,5))
			except AttributeError as e:
				error = "Not valid save file - did you select file 'SaveGameInfo' instead of 'playername_number'?"
				return render_template("index.html", error=error, recents=get_recents(), processtime=round(time.time()-start_time,5))
			g.db = connect_db()
			cur = g.db.cursor()
			dupe = is_duplicate(md5_info,player_info)
			if dupe != False:
				session[dupe] = md5_info
				return redirect(url_for('display_data',url=dupe))
			else:
				farm_info = getFarmInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
				outcome, error = insert_info(player_info,farm_info,md5_info)
				process_queue()
			g.db.close()
			if outcome != False:
				session[outcome] = md5_info
				return redirect(url_for('display_data',url=outcome))
	return render_template("index.html", recents=get_recents(), error=error, processtime=round(time.time()-start_time,5))

def connect_db():
	return sqlite3.connect(app.database)

def get_recents():
	g.db = connect_db()
	cur = g.db.cursor()
	cur.execute('SELECT url, name, farmName, date, avatar_url, farm_url FROM playerinfo ORDER BY id DESC LIMIT 12')
	recents = cur.fetchall()
	g.db.close()
	if len(recents)==0:
		recents == None
	return recents

def is_duplicate(md5_info,player_info):
	cur = g.db.cursor()
	cur.execute('SELECT id, md5, name, uniqueIDForThisGame, url FROM playerinfo WHERE md5=?',(md5_info,))
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
	player_info['date'] = ['Spring','Summer','Autumn','Winter'][(((player_info['stats']['DaysPlayed']%(28*4))-((player_info['stats']['DaysPlayed']%(28*4))%(28)))/28)]+' '+str((player_info['stats']['DaysPlayed']%(28*4))%(28))+', Year '+str(((player_info['stats']['DaysPlayed']-player_info['stats']['DaysPlayed']%(28*4))/(28*4))+1)
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
	questionmarks = ('?,'*len(values))[:-1]
	try:
		g.db.execute('INSERT INTO playerinfo ('+colstring+') VALUES ('+questionmarks+')',tuple(values))
		cur = g.db.cursor()
		cur.execute('SELECT id,added_time FROM playerinfo WHERE uniqueIDForThisGame=? AND name=? AND md5 =?',(player_info['uniqueIDForThisGame'],player_info['name'],md5_info))
		row = cur.fetchone()
		url = dec2big(int(row[0])+int(row[1]))
		rowid = row[0]
		cur.execute('UPDATE playerinfo SET url=? WHERE id=?',(url,rowid))
		g.db.execute('INSERT INTO todo (task, playerid) VALUES (?,?)',('process_image',rowid))
		g.db.commit()
		return url, None
	except sqlite3.OperationalError as e:
		g.db.execute('INSERT INTO errors (ip, time, notes) VALUES (?,?,?)',(request.environ['REMOTE_ADDR'], time.time(),str(e)+' '+str([columns,values])))
		g.db.commit()
		return False, "Save file incompatible with current database; saving for admins to review (please check back later)"

@app.route('/<url>')
def display_data(url):
	error = None
	deletable = None
	start_time = time.time()
	g.db = connect_db()
	cur = g.db.cursor()
	cur.execute('SELECT '+database_fields+' FROM playerinfo WHERE url=?',(url,))
	data = cur.fetchall()
	if len(data) != 1:
		error = 'There is nothing here... is this URL correct?'
		g.db.execute('INSERT INTO errors (ip, time, notes) VALUES (?,?,?)',(request.environ['REMOTE_ADDR'],time.time(),str(len(data))+' cur.fetchall() for url:'+str(url)))
		g.db.commit()
		return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))
	else:
		cur.execute('UPDATE playerinfo SET views=views+1 WHERE url=?',(url,))
		g.db.commit()
		datadict = {}
		for k, key in enumerate(sorted(database_structure_dict.keys())):
			if key != 'farm_info':
				datadict[key] = data[0][k]

		if url in session:
			cur.execute('SELECT url,md5,del_token FROM playerinfo WHERE uniqueIDForThisGame=? AND name=? AND farmName=?',(datadict['uniqueIDForThisGame'],datadict['name'],datadict['farmName']))
			md5_from_db = cur.fetchall()
			if session[url] in [md5[1] for md5 in md5_from_db]:
				deletable = True
				for row in md5_from_db:
					session[row[0]] = row[1]
					session[row[0]+'del_token'] = row[2]

		datadict['money'] = "{:,}".format(datadict['money'])
		datadict['totalMoneyEarned'] = "{:,}".format(datadict['totalMoneyEarned'])

		friendships = sorted([[friendship[11:],datadict[friendship]] for friendship in sorted(database_structure_dict.keys()) if friendship.startswith('friendships') and datadict[friendship]!=None],key=lambda x: x[1])[::-1]
		kills = sorted([[kill[27:].replace('_',' '),datadict[kill]] for kill in sorted(database_structure_dict.keys()) if kill.startswith('statsSpecificMonstersKilled') and datadict[kill]!=None],key=lambda x: x[1])[::-1]
		cur.execute('SELECT url, date FROM playerinfo WHERE uniqueIDForThisGame=? AND name=? AND farmName=?',(datadict['uniqueIDForThisGame'],datadict['name'],datadict['farmName']))
		other_saves = sorted(cur.fetchall(),key=lambda x: x[1])
		return render_template("profile.html", deletable=deletable, data=datadict, kills=kills, friendships=friendships, others=other_saves, error=error, processtime=round(time.time()-start_time,5))

@app.route('/<url>/<instruction>')
def operate_on_url(url,instruction):
	error = None
	deletable = None
	start_time = time.time()
	if url in session:
		g.db = connect_db()
		cur = g.db.cursor()
		cur.execute('SELECT id,md5,del_token,url FROM playerinfo WHERE uniqueIDForThisGame=(SELECT uniqueIDForThisGame FROM playerinfo WHERE url=?)',(url,))
		data = cur.fetchall()
		print data
		if instruction == 'del':
			for row in data:
				if session[url] == row[1] and session[url+'del_token'] == row[2]:
					g.db.execute('DELETE FROM playerinfo WHERE id=(?)',(row[0],))
					g.db.commit()
					session.pop(url,None)
					session.pop(url+'del_token',None)
					return redirect(url_for('home'))
			return render_template("error.html", error="Your session validation data is wrong", processtime=round(time.time()-start_time,5))
		elif instruction == 'delall':
			for row in data:
				if not (session[row[3]] == row[1] and session[url+'del_token']):
					return render_template("error.html", error="Session validation data was wrong for at least one resource", processtime=round(time.time()-start_time,5))
			for row in data:
				g.db.execute('DELETE FROM playerinfo WHERE id=(?)',(row[0],))
				session.pop(row[3],None)
				session.pop(row[3]+'del_token',None)
			g.db.commit()
			return redirect(url_for('home'))
	else:
		return render_template("error.html", error="Unknown instruction or insufficient credentials", processtime=round(time.time()-start_time,5))


	#db.execute('DELETE FROM todo WHERE id=(?)',(task[0],))


if __name__ == "__main__":
	app.run(debug=True)