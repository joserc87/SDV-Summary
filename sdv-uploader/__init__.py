from windows import launch
from setup import version
import os
import sys
import logging

__version__ = version

def main():
	try:
		logging.debug('trying to change to directory...')
		directory = os.path.split(sys.argv[0])[0]
		os.chdir(directory)
		logging.debug('changed directory to {}'.format(directory))
	except:
		pass
	logging.debug('launching...')
	launch()

if __name__ == '__main__':
	main()