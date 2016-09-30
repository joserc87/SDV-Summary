import os

from .renderTiles import TileMap


base_path = os.getcwd() + os.path.join(os.path.sep, 'sdv', 'assets')

def generateBase(assets, mapData, season, type):
    tileMap = TileMap(mapData)
    tileMap.processData()
    dest = os.path.join('base', type, season)
    tileMap.renderData(os.path.join(base_path, dest), season)

def generateBases():
    types = [
        'Combat',
        'Fishing',
        'Foraging',
        'Mining',
        'default'
    ]

    seasons = [
        'spring',
        'summer',
        'fall',
        'winter'
    ]

    for season in seasons:
        for type in types:
            print(type, season)
            if type == 'default':
                farm = 'Farm.tbin'
            else:
                farm = 'Farm_{0}.tbin'.format(type)
            dataLoc = os.getcwd() + os.path.join(os.path.sep, 'assets', 'Maps', farm)
            generateBase(None, dataLoc, season, type)