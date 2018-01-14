import sys
import os

if sys.platform == 'win32':
	import winreg
elif sys.platform == 'darwin':
	import plistlib
else:
	raise ImportError


REGISTRY_NAME = 'uploadfarm'
MAC_APP_LABEL = "farm.upload.uploader".format(REGISTRY_NAME)
MAC_PLIST_LOCATION = os.path.expanduser('~/Library/LaunchAgents/{}.plist'.format(MAC_APP_LABEL))
 

def add_to_startup(filename='"{}" --silent'.format(os.path.abspath(sys.argv[0]))):
	if sys.platform == 'win32':
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
		winreg.SetValueEx(key, REGISTRY_NAME, 0, winreg.REG_SZ, filename)
		key.Close()
	elif sys.platform == 'darwin':
		create_plist_mac(filename,True)


def create_plist_mac(filename,state):
	plist_info = {'ProgramArguments': filename.split(' '),
		'ProcessType': 'Interactive', 'Label': MAC_APP_LABEL,
		'KeepAlive': False, 'RunAtLoad': state}
	os.makedirs(MAC_PLIST_LOCATION,exist_ok=True)
	with open(MAC_PLIST_LOCATION,'wb') as f:
		plistlib.dump(plist_info,f)


def update_plist_mac(state):
	if check_startup() != state:
		try:
			with open(MAC_PLIST_LOCATION,'rb') as f:
				plist_info = plistlib.load(f)
			plist_info['RunAtLoad'] = state
			with open(MAC_PLIST_LOCATION,'wb') as f:
				plistlib.dump(plist_info, f)
		except FileNotFoundError:
			create_plist_mac(state)


def remove_from_startup():
	if sys.platform == 'win32':
		try:
			key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
			winreg.DeleteValue(key, REGISTRY_NAME)
			key.Close()
		except:
			pass
	elif sys.platform == 'darwin':
		update_plist_mac(False)



def check_startup():
	if sys.platform == 'win32':
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_READ)
		i = 0
		while True:
			try:
				a = winreg.EnumValue(key,i)
				i+=1
				if a[0] == REGISTRY_NAME:
					return True
			except OSError:
				break
		key.Close()
		return False
	elif sys.platform == 'darwin':
		try:
			with open(MAC_PLIST_LOCATION,'rb') as f:
				a = plistlib.load(f)
			return a['RunAtLoad']
		except FileNotFoundError:
			return False

def main():
	print(check_startup())
	add_to_startup()
	print(check_startup())
	remove_from_startup()
	print(check_startup())


if __name__ == '__main__':
	main()