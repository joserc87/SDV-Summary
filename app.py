#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request, flash, g
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

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
app.database = 'sdv.db'

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
			player_info = playerInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			g.db = connect_db()
			cur = g.db.cursor()
			dupe = is_duplicate(md5_info,player_info)
			if dupe != False:
				return redirect(url_for('display_data',url=dupe))
			else:
				farm_info = getFarmInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
				outcome, error = insert_info(player_info,farm_info,md5_info)
				#note to self: need to have better handling for this, this is just a stop-gap!
			g.db.close()
			if outcome != False:
				return redirect(url_for('display_data',url=outcome))
	return render_template("index.html", error=error, processtime=round(time.time()-start_time,5))

def connect_db():
	return sqlite3.connect(app.database)

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
	#columns.append('url')
	#values.append(dec2big(int(time.time())))
	print 'WARNING USING dec2big OF time.time() FOR URL! THIS IS _NOT_ RIGOROUS!'
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

	#print columns
	#print values
	colstring = ''
	for c in columns:
		colstring += c+', '
	colstring = colstring[:-2]
	questionmarks = ('?,'*len(values))[:-1]
	#print tuple(columns+values)
	try:
		g.db.execute('INSERT INTO playerinfo ('+colstring+') VALUES ('+questionmarks+')',tuple(values))
		cur = g.db.cursor()
		cur.execute('SELECT id,added_time FROM playerinfo WHERE uniqueIDForThisGame=? AND name=? AND md5 =?',(player_info['uniqueIDForThisGame'],player_info['name'],md5_info))
		row = cur.fetchone()
		url = dec2big(int(row[0])+int(row[1]))
		rowid = row[0]
		cur.execute('UPDATE playerinfo SET url=? WHERE id=?',(url,rowid))
		#g.db.commit()
		#cur.execute('SELECT id,url FROM playerinfo WHERE uniqueIDForThisGame=? AND name=? AND md5 =?',(player_info['uniqueIDForThisGame'],player_info['name'],md5_info))
		#row = cur.fetchall()[-1]
		g.db.execute('INSERT INTO todo VALUES (?,?)',('process_image',rowid))
		g.db.commit()
		return url, None
	except sqlite3.OperationalError:
		g.db.execute('INSERT INTO errors VALUES (?,?)',(time.time(),str([columns,values])))
		g.db.commit()
		return False, "Save file incompatible with current database; saving for admins to review (please check back later)"

@app.route('/<url>')
def display_data(url):
	error = None
	start_time = time.time()
	g.db = connect_db()
	cur = g.db.cursor()
	cur.execute('SELECT * FROM playerinfo WHERE url=?',(url,))
	data = cur.fetchall()
	if len(data) != 1:
		g.db.execute('INSERT INTO errors VALUES (?,?)',(time.time(),'nonunity cur.fetchall() for url:'+str(url)))
	else:
		return render_template("profile.html", data=data, error=error, processtime=round(time.time()-start_time,5))


@app.route('/upload',methods=['GET','POST'])
def upload():
	return 'wat'



if __name__ == "__main__":
	app.run(debug=True)