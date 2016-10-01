import os
import errno

from .farm import copy_farm
from .bases import generateBases

# TODO: merge pets and partners to NPCs
from .partners import copy_partners
from .pets import copy_pets

base_path = os.getcwd() + os.path.join(os.path.sep, 'sdv', 'assets')


def create_directories():

    types = [
        'Combat',
        'Fishing',
        'Foraging',
        'Mining',
        'Default'
    ]

    seasons = [
        'spring',
        'summer',
        'fall',
        'winter'
    ]

    directories = [
        'base',
        'farm',
        os.path.join('farm', 'buildings'),
        os.path.join('farm', 'terrainFeatures'),
        os.path.join('farm', 'looseSprites'),
        os.path.join('farm', 'tileSheets'),
        'npcs',
        os.path.join('npcs', 'partners'),
        os.path.join('npcs', 'animals'),
        'player',
        os.path.join('player', 'male'),
        os.path.join('player', 'female'),
        os.path.join('player', 'misc')
    ]

    for season in seasons:
        for type in types:
            directories.append(os.path.join('base', type, season))

    for directory in directories:
        try:
            os.makedirs(os.path.join(base_path, directory))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # TODO: clean this up
    path = os.getcwd() + os.path.join(os.path.sep, 'sdv',)
    try:
        os.makedirs(os.path.join(path, 'uploads'))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def copy_assets():
    create_directories()
    copy_farm()
    copy_partners()
    generateBases()
    copy_pets()