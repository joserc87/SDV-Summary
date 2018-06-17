import os
import json
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from database import md5, check_monitor, update_monitor, add_log_entry, get_monitor_data_by_name
from handler import archive

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('uploader.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.debug('launched with arguments {}'.format(sys.argv))

class Watcher:
	def __init__(self,path_to_watch,backup_dir):
		logger.debug('Watcher:__init__: path to watch {}, backup_dir {}'.format(path_to_watch,backup_dir))
		self.path_to_watch = path_to_watch
		os.makedirs(path_to_watch,exist_ok=True)
		os.makedirs(backup_dir,exist_ok=True)
		logger.debug('Watcher:__init__: made or skipped over making directories')
		self.backup_dir = backup_dir
		logger.debug('Watcher:__init__: initializing watcher')
		self.initialize()
		logger.debug('Watcher:__init__: done initializing')


	def initialize(self):
		logger.debug('Watcher:initialize: getting observer')
		self.observer = Observer()
		logger.debug('Watcher:initialize: creating uploadfarmeventhandler')
		self.event_handler = UploadFarmEventHandler(self.path_to_watch,self.backup_dir)
		logger.debug('Watcher:initialize: adding schedule to observer')
		self.observer.schedule(self.event_handler,self.path_to_watch,recursive=True)


	def run(self,**kwargs):
		logger.debug('Watcher:run: run with kwargs {}'.format(kwargs))
		self.event_handler.set_kwargs(kwargs)
		logger.debug('Watcher:run: starting observer')
		self.observer.start()
		logger.debug('Watcher:run: started observer')
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			self.observer.stop()
		self.observer.join()
		logger.debug('Watcher:run: observer.joined()')


class UploadFarmEventHandler(FileSystemEventHandler):
	'''
	on change:
	1. reads current db monitor list
	2. if file is being monitored, copies file zipped to backup dir
	3. queues upload job
	'''
	def __init__(self,path_to_watch,backup_dir):
		super().__init__()
		logger.debug('UploadFarmEventHandler:__init__: initializing with path_to_watch {} and backup_dir {}'.format(path_to_watch,backup_dir))
		self.path_to_watch = path_to_watch
		self.backup_dir = backup_dir

	def set_kwargs(self,kwargs):
		self.kwargs = kwargs

	def on_modified(self,event):
		logger.debug('UploadFarmEventHandler:on_modified: triggered')
		if self.kwargs.get('function'):
			logger.debug('UploadFarmEventHandler:on_modified: triggered function')
			self.kwargs.get('function')()
		full_filename = os.path.join(self.path_to_watch,event.src_path)
		# print('changed: {}'.format(full_filename))
		logger.debug('UploadFarmEventHandler:on_modified: change detected in {}'.format(full_filename))
		monitor_comparison = check_monitor(full_filename)
		logger.debug('UploadFarmEventHandler:on_modified: monitor comparison {}'.format(monitor_comparison))
		if len(monitor_comparison) == 1:
			logger.debug('UploadFarmEventHandler:on_modified: entered try block')
			try:
				outcome = check_md5_and_process(monitor_comparison,full_filename,self.backup_dir)
				logger.debug('UploadFarmEventHandler:on_modified: outcome {}'.format(outcome))
				if outcome == True:
					if self.kwargs.get('signal'):
						self.kwargs.get('signal').emit()
			except FileNotFoundError as e:
				logger.error('UploadFarmEventHandler:on_modified: filenotfounderror {}'.format(e))
				pass


def manual_process(name,backup_dir):
	try:
		logger.debug('manual_process: entered try block')
		file_data = get_monitor_data_by_name(name)
		logger.debug('manual_process: got file_data {}'.format(file_data))
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
	watcher = Watcher('.','TEMP_BACKUPS')
	watcher.run()

if __name__ == "__main__":
	main()