import os
import errno

from .farm import copy_farm
from .partners import copy_partners

base_path = os.getcwd() + os.path.join(os.path.sep, 'sdv', 'assets')


def create_directories():
    directories = [
        'base',
        'farm',
        os.path.join('farm', 'buildings'),
        os.path.join('farm', 'terrainFeatures'),
        os.path.join('farm', 'looseSprites'),
        os.path.join('farm', 'tileSheets'),
        'partners',
        'pets',
        'player'
    ]

    for directory in directories:
        try:
            os.makedirs(os.path.join(base_path, directory))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def copy_assets():
    create_directories()
    copy_farm()
    copy_partners()