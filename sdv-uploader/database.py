import os
import glob
import hashlib
import time
import json
import sqlite3
import sys

from config import root_directory

def get_current_savegame_filenames(**kwargs):
	#look in registry? or just at appdata?
	if sys.platform == 'win32':
		savegamedir = os.path.join(os.getenv('APPDATA'),'StardewValley\\Saves')
	if sys.platform == 'darwin':
		savegamedir = os.path.expanduser('~/.config/StardewValley/Saves')
	else:
		raise SystemError
	lookin = os.path.join(savegamedir,'*')

	savegames = {}
	for row in [i for i in glob.glob(lookin) if os.path.isdir(i)]:
		savefolder = os.path.join(row,'*')
		dircontents = [[os.path.split(os.path.split(j)[0])[1],os.path.split(j)[1]] for j in glob.glob(savefolder)]
		if any([k[0]==k[1] for k in dircontents]) and any([k[1]=='SaveGameInfo' for k in dircontents]):
			name = [k[0] for k in dircontents if k[0]==k[1]]
			savegames[name[0]] = os.path.join(row,name[0])
	return savegamedir, savegames

def md5(filename):
	# start_time=time.time()
	h = hashlib.md5()
	with open(filename,'rb') as md5file:
		for chunk in iter(lambda: md5file.read(4096), b""):
			h.update(chunk)
	# print 'md5 took:',time.time()-start_time
	return h.hexdigest()


def check_settings():
	db = connect_db()
	c = db.cursor()
	try:
		get_user_info()
		return True
	except (sqlite3.OperationalError, IndexError):
		create_db()
		return False


def get_user_info():
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT id, email, token, refresh_token, expiry, info_json, settings_json, invalidated_refresh_token FROM settings ORDER BY id DESC')
	result = c.fetchall()
	return result[0]


def set_user_info(userinfodict):
	db = connect_db()
	c = db.cursor()
	keystring = ''
	updatestring = ''
	valuestring = ''
	values = []
	for key, value in userinfodict.items():
		if key in ['email','token','refresh_token','expiry','info_json','settings_json','invalidated_refresh_token']:
			keystring+='{},'.format(key)
			valuestring+='?,'
			updatestring+='{}=?,'.format(key)
			values.append(value)
	if len(values)>0:
		c.execute('SELECT Count(*) FROM settings')
		num_entries = c.fetchone()[0]
		if num_entries == 0:
			c.execute('INSERT INTO settings({}) VALUES ({})'.format(keystring[:-1],valuestring[:-1]),tuple(values))
		else:
			c.execute('UPDATE settings SET {}'.format(updatestring[:-1]),tuple(values))
		db.commit()
	else:
		raise IndexError
	db.close()

def clear_user_info():
	db = connect_db()
	c = db.cursor()
	c.execute('DELETE FROM settings')
	db.commit()
	db.close()

def is_user_info_invalid():
	try:
		return get_user_info()[7]
	except:
		return False

def create_db():
	try:
		idcode='INTEGER PRIMARY KEY AUTOINCREMENT'
		structure_dict = {'id':idcode,
		'email':'TEXT',
		'token':'TEXT',
		'refresh_token':'TEXT',
		'expiry':'INT',
		'info_json':'TEXT',
		'settings_json':'TEXT',
		'invalidated_refresh_token':'BOOLEAN DEFAULT 0'}

		monitor_dict = {'id':idcode,
		'name':'TEXT',
		'file':'TEXT',
		'monitoring':'BOOLEAN DEFAULT 1',
		'info_json':'TEXT',
		'uploading':'BOOLEAN DEFAULT 1'}

		log_dict = {'id':idcode,
		'time':'TEXT',
		'name':'TEXT',
		'file':'TEXT',
		'zipfile':'TEXT',
		'info_json':'TEXT',
		'uploadable':'BOOLEAN',
		'uploaded':'BOOLEAN DEFAULT 0'}

		structure = ''
		for key in sorted(structure_dict.keys()):
			structure += key + ' ' +structure_dict[key] + ',\n'
		structure = structure[:-2]

		log = ''
		for key in sorted(log_dict.keys()):
			log += key + ' ' +log_dict[key] + ',\n'
		log = log[:-2]

		monitor = ''
		for key in sorted(monitor_dict.keys()):
			monitor += key + ' ' +monitor_dict[key] + ',\n'
		monitor += ' UNIQUE(name)'

		connection=connect_db()
		c=connection.cursor()
		c.execute('CREATE TABLE settings('+structure+')')
		c.execute('CREATE TABLE log('+log+')')
		c.execute('CREATE TABLE monitor('+monitor+')')
		connection.commit()
		connection.close()
		return True
	except:
		return False


def get_monitors():
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT name, file, info_json, id, monitoring, uploading FROM monitor ORDER BY id DESC')
	monitors = c.fetchall()
	db.close()
	return monitors

def set_monitors():
	savegamedir, savegames = get_current_savegame_filenames()
	_set_monitors_from_savegames(savegames)


def _set_monitors_from_savegames(savegames):
	_set_monitors([[key,value] for key,value in savegames.items()])


def _set_monitors(list_of_files):
	'''
	takes list of name, file; inserts into db
	'''
	db = connect_db()
	c = db.cursor()
	for item in list_of_files:
		c.execute('INSERT OR IGNORE INTO monitor(name,file) VALUES(?,?)',(item[0],item[1]))
	db.commit()
	db.close()


def check_monitor(file):
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT name, info_json, id, uploading FROM monitor WHERE file = ? AND monitoring = 1',(file,))
	results = c.fetchall()
	assert len(results) < 2
	return results


def get_monitor_data_by_name(name):
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT name, info_json, id, uploading, file FROM monitor WHERE name = ?',(name,))
	results = c.fetchall()
	assert len(results) < 2
	return results


def update_monitor(name,**kwargs):
	db = connect_db()
	c = db.cursor()
	fields = ''
	valuelist = []
	for field in ['info_json','name','monitoring','uploading','file']:
		if kwargs.get(field) != None:
			fields += '{} = ?,'.format(field)
			valuelist.append(kwargs.get(field))
	valuelist.append(name)
	c.execute('UPDATE monitor SET '+fields[:-1]+' WHERE name = ?',tuple(valuelist))
	db.commit()
	db.close()


def add_log_entry(name,file,zipfile,info_json,uploadable):
	db = connect_db()
	c = db.cursor()
	c.execute('INSERT INTO log(time,name,file,zipfile,info_json,uploadable) VALUES (?,?,?,?,?,?)',
		(str(time.time()),name,file,zipfile,info_json,uploadable))
	db.commit()
	db.close()


def get_latest_log_entry_for(name,**kwargs):
	db = connect_db()
	c = db.cursor()
	refine_search = ''
	if 'successfully_uploaded' == True:
		refine_search = 'AND uploaded = 1 '
	c.execute('SELECT info_json, uploadable, uploaded FROM log WHERE name=? '+refine_search+'ORDER BY time DESC LIMIT 1',(name,))
	try:
		entry = c.fetchone()
		result = json.loads(entry[0])
		uploadable = entry[1]
		uploaded = entry[2]
	except (json.JSONDecodeError,TypeError):
		result = {}
		uploadable = None
		uploaded = None
	return result, uploadable, uploaded

def get_uploadables():
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT id, zipfile FROM log WHERE uploadable = 1 AND uploaded = 0 ORDER BY time ASC')
	results = c.fetchall()
	return results


def set_uploaded(rowid,url):
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT info_json FROM log WHERE id = ?',(rowid,))
	result = c.fetchone()
	info = json.loads(result[0])
	info['url'] = url
	info_json = json.dumps(info)
	c.execute('UPDATE log SET uploaded = 1, info_json = ? WHERE id = ?',(info_json,rowid))
	db.commit()
	db.close()


def connect_db():
	connection = sqlite3.connect(os.path.join(root_directory,'uploader.db'))
	return connection


def main():
	pass

if __name__=='__main__':
	main()