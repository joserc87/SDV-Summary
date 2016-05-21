import sys
from uploadfarm.tools.createdb import initialisedb, updatedb
from uploadfarm.tools.createadmin import initialiseAdmin

if __name__ == '__main__':
    if sys.version_info >= (3, 0):
        raw_input = input

    if raw_input('Initialise admin tables? (y/n)') == 'y':
            initialiseAdmin()
    if raw_input('Initialise data tables? (y/n)') == 'y':
            initialisedb()
    if raw_input('Update tables? (y/n)') == 'y':
            updatedb()
