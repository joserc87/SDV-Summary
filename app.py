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

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
app.database = 'sdv.db'


@app.route('/',methods=['GET','POST'])
def home():
	start_time = time.time()
	error = None
	if request.method == 'POST':
		inputfile = request.files['file']
		if inputfile:
			filename = secure_filename(inputfile.filename)
			inputfile.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			player_info = playerInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			farm_info = getFarmInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			error = insert_info(player_info,farm_info)
			#note to self: need to have better handling for this, this is just a stop-gap!
	return render_template("index.html", error=error, processtime=round(time.time()-start_time,5))

def connect_db():
	return sqlite3.connect(app.database)

def insert_info(player_info,farm_info):
	columns = []
	values = []
	columns.append('url')
	values.append(dec2big(int(time.time())))
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
	g.db = connect_db()
	print columns
	#print values
	colstring = ''
	for c in columns:
		colstring += c+', '
	colstring = colstring[:-2]
	questionmarks = ('?,'*len(values))[:-1]
	#print tuple(columns+values)
	try:
		g.db.execute('INSERT INTO playerinfo ('+colstring+') VALUES ('+questionmarks+')',tuple(values))
		g.db.commit()
		g.db.close()
		return None
	except sqlite3.OperationalError:
		g.db.execute('INSERT INTO errors VALUES (?,?)',(time.time(),str([columns,values])))
		g.db.commit()
		g.db.close()
		return "Save file incompatible with current database; saving for admins (please check back later)"


@app.route('/upload',methods=['GET','POST'])
def upload():
	return 'wat'



if __name__ == "__main__":
	app.run(debug=True)