import os
import time

import defusedxml
from xml.etree.ElementTree import ParseError

from playerInfo import get_player_info
from savefile import Savefile
from zipuploads import zopen, zwrite
from getDate import get_date

def archive(filename,backup_directory):
	'''
	takes filename, backup directory; copies zipped file to backup directory
	'''
	with open(filename,'rb') as f:
		data = f.read()

	stripped_filename = os.path.split(filename)[1]
	metadata = get_metadata_from_data(data)
	date = metadata.get('dateStringForSaveGame',get_date(metadata))

	write_filename = '{} [{} - {}].zip'.format(stripped_filename,date,int(time.time()))
	target = os.path.join(backup_directory,write_filename)
	try:
		zwrite(data,target,stripped_filename)
	except FileNotFoundError:
		os.makedirs(backup_directory)
		zwrite(data,target,stripped_filename)
	return stripped_filename, filename, target, metadata, date


def get_metadata_from_data(data):
	try:
		player_info = get_player_info(Savefile(data,True))
		return player_info
	except (defusedxml.common.EntitiesForbidden,IOError,AttributeError,ParseError):
		return None

def main():
	pass

if __name__ == "__main__":
	main()