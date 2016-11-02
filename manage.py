#!/usr/bin/env python
import sys
import subprocess
from flask_script import Manager
from sdv import app
from sdv.createdb import init_db
from sdv.createadmin import init_admin
from tools import copy_assets
import os

manager = Manager(app)


@manager.command
def createdb(drop_all=False):
    """Initialise Database."""
    init_db(drop_all)

@manager.command
def createadmin(drop_all=False):
    """Initialise Admin DB."""
    init_admin()

@manager.command
def test():
    """Run Unit Tests."""
    tests = subprocess.call(['python', '-c', 'import tests; tests.run()'])
    sys.exit(tests)


@manager.command
def lint():
    """Run Flake8 Linter."""
    lint = subprocess.call(['python', '-m', 'flake8', '--ignore=E402', 'sdv/',
                            'manage.py']) == 0
    if lint:
        print('OK')
    sys.exit(lint)

@manager.command
def init():
    """Copy game assets from folder"""
    copy_assets()

if __name__ == "__main__":    
    # print('os.chdir coming up... if the program refuses to run, comment it out, manage.py runserver, then uncomment and save')
    # os.chdir(os.path.join(os.path.dirname(__file__),"sdv"))
    # sys.path.insert(0, './')
    # sys.path.insert(0, './sdv')
    manager.run()
