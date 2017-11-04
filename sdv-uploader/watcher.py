import threading
# from multiprocessing import Process
from database import create_db, get_current_savegame_filenames, set_monitors
from watcherlib import Watcher

LOCAL_BACKUP_DIR = 'backups'

def launch_watcher_as_thread(backupdir=LOCAL_BACKUP_DIR,signal=None):
	t = threading.Thread(target=_start_watcher,args=(backupdir,signal))
	t.setDaemon(True)
	t.start()
	return t

def _start_watcher(backupdir,signal):
	savegamedir = initialization()
	w = Watcher(savegamedir,backupdir)
	w.run(function=set_monitors,signal=signal)
	return w

def initialization():
	savegamedir, savegames = get_current_savegame_filenames()
	if create_db() == True:
		# if just created db, add all savegames to it
		set_monitors()
	return savegamedir

def main():
	t = launch_watcher_as_thread()
	input('press key to end monitoring')

if __name__ == "__main__":
	main()