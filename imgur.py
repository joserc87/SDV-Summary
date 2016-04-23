from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from app import app, connect_db
from flask import url_for
import uuid
import json

def checkApiAccess(userid):
	# something that checks whether we have api keys and whether they work;
	# if not, return False
	print 'checkApiAccess needs not to have this silly userid==test thing...'
	if userid == 'test':
		access_token = app.config['IMGUR_ACCESS_TOKEN']
		refresh_token = app.config['IMGUR_REFRESH_TOKEN']
	else:
		db = connect_db()
		c = db.cursor()
		c.execute('SELECT imgur_json FROM users WHERE id='+app.sqlesc,(userid,))
		r = c.fetchone()
		if len(r) > 0:
			try:
				r = json.loads(r[0])
				access_token = r['access_token']
				refresh_token = r['refresh_token']
			except TypeError:
				return False
		else:
			return False
	client = ImgurClient(app.config['IMGUR_CLIENTID'],app.config['IMGUR_SECRET'])
	client.set_user_auth(access_token,refresh_token)
	try:
		print client.get_account('me').url
		print client.credits
		return True
	except ImgurClientError:
		return False

def getAuthUrl(userid):
	db = connect_db()
	c = db.cursor()
	imgur_id = unicode(uuid.uuid4())
	c.execute('UPDATE users SET imgur_id='+app.sqlesc+' WHERE id='+app.sqlesc,(imgur_id,userid))
	db.commit()
	db.close()
	client = ImgurClient(app.config['IMGUR_CLIENTID'],app.config['IMGUR_SECRET'])
	authorization_url = client.get_auth_url('code')+'&state='+unicode(imgur_id)
	return authorization_url

def swapCodeForTokens(response):
	# takes dict of response parameters as input, like {'error':'blah blah'} or {'code':'blah blah','state':'blah blah'}
	db = connect_db()
	c=db.cursor()
	if 'error' in response:
		c.execute('UPDATE users SET imgur_json=NULL WHERE imgur_id='+app.sqlesc,(response['state'],))
		db.commit()
		return False
	# called at the server redirect when imgur returns the code
	client = ImgurClient(app.config['IMGUR_CLIENTID'],app.config['IMGUR_SECRET'])
	credentials = client.authorize(response['code'],'authorization_code')
	# print credentials
	if 'access_token' in credentials.keys() and 'refresh_token' in credentials.keys():
		db = connect_db()
		c = db.cursor()
		c.execute('UPDATE users SET imgur_json='+app.sqlesc+' WHERE imgur_id='+app.sqlesc,(json.dumps(credentials),response['state']))
		db.commit()
		db.close()
		return True
	else:
		c.execute('UPDATE users SET imgur_json=NULL WHERE imgur_id='+app.sqlesc,(response['state'],))
		db.commit()
		return False

def uploadToImgur(userid,url):
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT map_url FROM playerinfo WHERE url='+app.sqlesc,(url,))
	map_url = c.fetchone()[0]
	# try:
	c.execute('SELECT imgur_json FROM users WHERE id='+app.sqlesc,(userid,))
	r = json.loads(c.fetchone()[0])
	access_token = r['access_token']
	refresh_token = r['refresh_token']
	client = ImgurClient(app.config['IMGUR_CLIENTID'],app.config['IMGUR_SECRET'])
	client.set_user_auth(access_token,refresh_token)
	# file = url_for('home',filename=map_url,_external=True)
	# print 'uploaded to',file
	# client.upload_from_url(file,config={'title':'uploaded from','description':'upload.farm'},anon=False)
	result = client.upload_from_path(map_url,config={'title':'uploaded from','description':'upload.farm'},anon=False)
	print result
	try:
		return result['link']
	except:
		return False


if __name__ == '__main__':
	code = ''
	state = ''
	if code == '':
		user_id = 1
		print 'this should be a token, not a raw db entry'
		check_auth = checkApiAccess(user_id)
		if check_auth == False:
			print getAuthUrl(user_id)
		else:
			print check_auth
	else:
		codedict = {'code':code,'state':state}
		swapCodeForTokens(codedict)
		

	file = './static/images/1AFQF1p.png'
	# print client.upload_from_path(file,config={'title':'uploaded from','description':'python'},anon=False)

	print client.get_account('me').id

	response_looks_like = {u'datetime': 1460205330, u'bandwidth': 0, u'nsfw': None,
	u'vote': None, u'id': u'68htuuP', u'account_id': 33971158, u'in_gallery': False,
	u'title': u'The Title', u'section': None, u'width': 80, u'size': 1638, u'type': u'image/png',
	u'deletehash': u'yHKPz1regUue88y', u'description': u'The Description', u'views': 0,
	u'link': u'http://i.imgur.com/68htuuP.png', u'height': 152, u'name': u'', u'favorite': False,
	u'account_url': None, u'comment_preview': None, u'animated': False}