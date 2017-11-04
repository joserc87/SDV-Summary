import os
import json

import win32file
import win32con

from database import md5, check_monitor, update_monitor, add_log_entry, get_monitor_data_by_name
from handler import archive

class Watcher:
	def __init__(self,path_to_watch,backup_dir):
		self.path_to_watch = path_to_watch
		self.backup_dir = backup_dir
		self.initialize()

	ACTIONS = {
		1:"Created",
		2:"Deleted",
		3:"Updated",
		4:"Renamed from something",
		5:"Renamed to something"
	}

	FILE_LIST_DIRECTORY = 0x0001

	def initialize(self):
		self.hDir = win32file.CreateFile(
			self.path_to_watch,
			self.FILE_LIST_DIRECTORY,
			win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
			None,
			win32con.OPEN_EXISTING,
			win32con.FILE_FLAG_BACKUP_SEMANTICS,
			None)

	def run(self,**kwargs):
		'''
		sits and waits for a directory change. on change:
		1. reads current db monitor list
		2. if file is being monitored, copies file zipped to backup dir
		3. queues upload job
		'''
		while True:
			results = win32file.ReadDirectoryChangesW(
				self.hDir,
				16384,
				True,
				win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
				win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
				win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
				win32con.FILE_NOTIFY_CHANGE_SIZE |
				win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
				win32con.FILE_NOTIFY_CHANGE_SECURITY,
				None,
				None)
			if kwargs.get('function'):
				kwargs.get('function')()
			for action, file in results:
				full_filename = os.path.join(self.path_to_watch,file)
				monitor_comparison = check_monitor(full_filename)
				if len(monitor_comparison) == 1:
					try:
						outcome = check_md5_and_process(monitor_comparison,full_filename,self.backup_dir)
						if outcome == True:
							if kwargs.get('signal'):
								kwargs.get('signal').emit()
					except FileNotFoundError:
						pass


def manual_process(name,backup_dir):
	try:
		file_data = get_monitor_data_by_name(name)
		filename = file_data[0][4]
		if len(file_data) == 1:
			outcome = check_md5_and_process(file_data,filename,backup_dir,force=True)
	except:
		pass


def check_md5_and_process(monitor_comparison,full_filename,backup_dir,**kwargs):
	try:
		info = json.loads(monitor_comparison[0][1])
	except:
		info = {}
	current_md5 = md5(full_filename)
	if current_md5 != info.get('md5',None) or ('force' in kwargs and kwargs.get('force')==True):
		name, file, zipfile, metadata, date = archive(full_filename,backup_dir)
		info['date'] = date
		info['metadata'] = metadata
		info['md5'] = current_md5
		info_json = json.dumps(info)
		update_monitor(monitor_comparison[0][0],info_json=info_json)
		uploadable = monitor_comparison[0][3]
		add_log_entry(name,file,zipfile,info_json,uploadable)
		return True
	else:
		return False



def main():
	pass

if __name__ == "__main__":
	main()