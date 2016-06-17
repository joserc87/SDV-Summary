#!/usr/bin/env python

from flask_script import Manager
from sdv import app
from sdv.createdb import init_db

manager = Manager(app)


@manager.command
def createdb(drop_all=False):
    init_db(drop_all)

if __name__ == "__main__":
    manager.run()
