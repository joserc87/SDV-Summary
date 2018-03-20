import os
import sys
import subprocess
import secrets

from pyinstallerresourcesupport import resource_path

server_location = "https://upload.farm"

if sys.platform == 'win32':
	root_directory = os.path.join(os.getenv('APPDATA'),'upload.farm uploader')
	gifsicle_executable = resource_path(os.path.join('gifsicle','gifsicle.exe'))
elif sys.platform == 'darwin':
	root_directory = os.path.expanduser('~/.config/upload.farm uploader')
	# try:
	# 	subprocess.run(['gifsicle'], shell=True)
	# 	gifsicle_executable = 'gifsicle'
	# except FileNotFoundError:
	gifsicle_executable = None
else:
	raise ImportError

os.makedirs(root_directory,exist_ok=True)

backup_directory = os.path.join(root_directory,'backups')

client_id = secrets.client_id
client_secret = secrets.client_secret