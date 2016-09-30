import os
from shutil import copy

base_path = os.getcwd() + os.path.join(os.path.sep, 'sdv', 'assets')


def copy_images(file_names, src, dest):
    src_directory = os.getcwd() + os.path.join(os.path.sep, 'assets', src)
    for file in file_names:
        try:
            copy(os.path.join(src_directory, file), os.path.join(base_path, dest))
        except Exception as e:
            print(e)


def rip_stones():
    # Pull Stones from objects.png
    pass


def copy_farm():
    buildings = [
        'Barn.png',
        'Big Barn.png',
        'Big Coop.png',
        'Coop.png',
        'Deluxe Barn.png',
        'Deluxe Coop.png',
        'Silo.png',
        'Slime Hutch.png',
        'Stable.png',
        'Well.png',
        'Houses.png'
    ]

    terrainFeatures = [
        'mushroom_tree.png',
        'tree1_fall.png',
        'tree1_spring.png',
        'tree1_summer.png',
        'tree1_winter.png',
        'tree2_fall.png',
        'tree2_spring.png',
        'tree2_summer.png',
        'tree2_winter.png',
        'tree3_fall.png',
        'tree3_spring.png',
        'tree3_winter.png',
        'flooring.png',
        'hoeDirt.png',
        'hoeDirtsnow.png',
        'grass.png'
    ]

    tileSheets = [
        'Craftables.png',
        'crops.png',
        'fruitTrees.png'
    ]

    maps = [
        'springobjects.png'
    ]

    looseSprites = [
        'Fence1.png',
        'Fence2.png',
        'Fence3.png',
        'Fence5.png'
    ]

    copy_images(buildings, 'Buildings', os.path.join('farm', 'buildings'))
    copy_images(terrainFeatures, 'TerrainFeatures', os.path.join('farm', 'terrainFeatures'))
    copy_images(tileSheets, 'TileSheets', os.path.join('farm', 'tileSheets'))
    copy_images(maps, 'Maps', os.path.join('farm', 'tileSheets'))
    copy_images(looseSprites, 'LooseSprites', os.path.join('farm', 'looseSprites'))
