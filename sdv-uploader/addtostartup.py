import sys
import os

if sys.platform == 'win32':
	import winreg
elif sys.platform == 'darwin':
	pass
else:
	raise ImportError


REGISTRY_NAME = 'uploadfarm'
MAC_APP_LABEL = "org.{}.uploader".format(REGISTRY_NAME)


def add_to_startup(filename='"{}" --silent'.format(sys.argv[0])):
	if sys.platform == 'win32':
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
		winreg.SetValueEx(key, REGISTRY_NAME, 0, winreg.REG_SZ, filename)
		key.Close()
	elif sys.platform == 'darwin':
		create_plist_mac(filename)

def create_plist_mac(filename):
	location = os.path.expanduser('~/Library/LaunchAgents/{}.plist'.format(MAC_APP_LABEL))
	args = filename.split(' ')

	program_arguments = ''
	for arg in args:
		program_arguments += '<string>{}</string>\n'.format(arg)

	plist = """<?xml version="1.0" encoding="UTF-8"?>
		<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
		<plist version="1.0">
		<dict>
		    <key>Label</key>
		    <!-- The label should be the same as the filename without the extension -->
		    <string>"""+MAC_APP_LABEL+"""</string>
		    <!-- Specify how to run your program here -->
		    <key>ProgramArguments</key>
		    <array>
		        """+program_arguments+"""
		    </array>
		    <key>ProcessType</key>
		    <string>Interactive</string>
		    <key>RunAtLoad</key>
		    <true/>
		    <key>KeepAlive</key>
		    <false/>
		</dict>
			</plist>"""
	print('writing to: {}'.format(location))
	print('content: {}'.format(plist))
	print('((NOT WRITTEN))')

def remove_from_startup():
	if sys.platform == 'win32':
		try:
			key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
			winreg.DeleteValue(key, REGISTRY_NAME)
			key.Close()
		except:
			pass
	elif sys.platform == 'darwin':
		pass


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
		return False


def main():
	print(check_startup())
	add_to_startup()
	print(check_startup())
	remove_from_startup()
	print(check_startup())


if __name__ == '__main__':
	main()