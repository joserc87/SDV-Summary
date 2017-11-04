import sys
import winreg

REGISTRY_NAME = 'uploadfarm'


def add_to_startup(filename='"{}" --silent'.format(sys.argv[0])):
	key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
	winreg.SetValueEx(key, REGISTRY_NAME, 0, winreg.REG_SZ, filename)
	key.Close()


def remove_from_startup():
	try:
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
		winreg.DeleteValue(key, REGISTRY_NAME)
		key.Close()
	except:
		pass


def check_startup():
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


def main():
	print(check_registry())
	add_to_registry()
	print(check_registry())
	remove_from_registry()
	print(check_registry())


if __name__ == '__main__':
	main()