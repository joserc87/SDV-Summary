import requests
import time

from config import client_id, client_secret, server_location
from database import get_user_info, set_user_info


def get_uploader_version():
	return _send_request('/api/v1/uploader_version',None,'GET')


def get_user_email():
	payload = _make_api_payload()
	return _send_request('/api/v1/get_user_info',payload)


def get_series_info(url):
	payload = _make_api_payload(url=url)
	return _send_request('/api/v1/get_series_info',payload)


def upload_zip(filename):
	payload = _make_api_payload()
	return _send_request_with_zipfile('/api/v1/upload_zipped',payload,filename)


def update_token():
	payload = _make_api_payload(refresh_token=_get_token(refresh_token=True))
	j = _send_request('/api/v1/refresh_token',payload)
	if 'token' in j:
		userinfodict = {'token':j['token'],
						'refresh_token':j['refresh_token'],
						'expiry':time.time()+j['expires_in']}
		set_user_info(userinfodict)
	else:
		userinfodict = j
	return userinfodict


def _send_request_with_zipfile(endpoint,api_payload,filename):
	try:
		r = requests.post(server_location+endpoint,data=api_payload,files={'zip':open(filename,'rb')},timeout=60)
		return _handle_response(r)
	except:
		return {'error':'unable to connect to server endpoint {}'.format(endpoint)}


def _send_request(endpoint,api_payload,method='POST'):
	try:
		if method=='POST':
			m = requests.post
		elif method == 'GET':
			m = requests.get
		r = m(server_location+endpoint,data=api_payload,timeout=5)
		return _handle_response(r)
	except requests.exceptions.ConnectionError:
		return {'error':'unable to connect to server endpoint {}'.format(endpoint)}

def _handle_response(r):
	try:
		j = r.json()
	except:
		return {}
	if not _valid_response(j):
		_handle_bad_token()
	return j

def _valid_response(j):
	if 'error' in j and j['error'] in ['bad_refresh_token','bad_token','no_api_access']:
		return False
	else:
		return True

def _handle_bad_token():
	set_user_info({'invalidated_refresh_token':True})


def _make_api_payload(**kwargs):
	api_payload = kwargs
	api_payload['client_id'] = client_id
	api_payload['client_secret'] = client_secret
	if 'refresh_token' not in kwargs:
		api_payload['token'] = _get_token()
	return api_payload


def _get_token(**kwargs):
	try:
		user_info = get_user_info()
		refresh_token = user_info[3]
		if kwargs.get('refresh_token') == True:
			return refresh_token
		token = user_info[2]
		expiry = user_info[4]
	except:
		raise IndexError('No settings were returned from the database')
	if expiry < time.time():
		token = update_token()['token']
	return token


def main():
	print(get_user_email())
	print(get_uploader_version())
	print(get_series_info('1B3RNh'))


if __name__ == "__main__":
	main()