#!/usr/bin/env python
import sys
import subprocess
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sdv import create_app
from sdv.models import db

app = create_app()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


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

if __name__ == "__main__":
    manager.run()
