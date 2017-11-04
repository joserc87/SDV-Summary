import time
import threading

from database import get_uploadables, set_uploaded
from ufapi import upload_zip, _valid_response

class UploadMonitor:
	def __init__(self,**kwargs):
		self.time_between_checks = 5 if 'time_between_checks' not in kwargs else kwargs['time_between_checks']
		self.error_signal = None if 'error_signal' not in kwargs else kwargs['error_signal']
		self.update_signal = None if 'update_signal' not in kwargs else kwargs['update_signal']

	def run(self):
		while True:
			self.run_once()
			time.sleep(self.time_between_checks)

	def run_once(self):
		for item in get_uploadables():
			result = upload_zip(item[1])
			if 'url' in result:
				set_uploaded(item[0],result['url'])
				self.emit_success()
			elif 'retry-next' in result:
				time.sleep(result['retry-next'])
			elif not _valid_response(result):
				self.emit_error()
			time.sleep(5)

	def emit_error(self):
		if self.error_signal:
			self.error_signal.emit()

	def emit_success(self):
		if self.update_signal:
			self.update_signal.emit()

def launch_uploadmonitor_as_thread(**kwargs):
	t = threading.Thread(target=_start_uploadmonitor,kwargs=kwargs)
	t.setDaemon(True)
	t.start()
	return t

def _start_uploadmonitor(**kwargs):
	w = UploadMonitor(**kwargs)
	w.run()
	return w

def main():
	u = UploadMonitor()
	u.run()

if __name__ == "__main__":
	main()