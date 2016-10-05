import os
from shutil import copy
from PIL import Image

base_path = os.getcwd() + os.path.join(os.path.sep, 'sdv', 'assets')


def copy_images(file_names, src, dest):
    src_directory = os.getcwd() + os.path.join(os.path.sep, 'assets', src)
    for file in file_names:
        try:
            copy(os.path.join(src_directory, file), os.path.join(base_path, dest))
        except Exception as e:
            print(e)


def copy_farm():
    buildings = [
        'Silo.png',
        'Slime Hutch.png',
        'Stable.png',
        'Well.png',
        'Houses.png',
        'Earth Obelisk.png',
        'Gold Clock.png',
        'Junimo Hut.png',
        'Shed.png',
        'Water Obelisk.png'
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

    # Crop and compose remaining asset

    # Mill
    src_directory = os.getcwd() + os.path.join(os.path.sep, 'assets')
    assets = Image.open(os.path.join(src_directory, 'Buildings', 'Mill.png'))

    mill = assets.crop((0, 0, 64, 128))
    blade = assets.crop((64,0, 64+32, 32))
    mill.paste(blade, box=(8,1), mask=blade)
    mill.save(os.path.join(base_path, 'farm', 'buildings', 'Mill.png'))

    # Barns

    # Normal
    assets = Image.open(os.path.join(src_directory, 'Buildings', 'Barn.png'))

    barn = assets.crop((0, 0, 112, 112))
    door = assets.crop((0, 112, 32, 112 + 16))
    darkness = assets.crop((32, 112, 32+32, 112 + 16))
    barn.paste(darkness, box=(48, 96), mask=darkness)
    barn.paste(door, box=(48, 88), mask=door)
    barn.save(os.path.join(base_path, 'farm', 'buildings', 'Barn.png'))

    # Big
    assets = Image.open(os.path.join(src_directory, 'Buildings', 'Big Barn.png'))

    barn = assets.crop((0, 0, 112, 112))
    door = assets.crop((0, 112, 32, 112 + 16))
    darkness = assets.crop((32, 112, 32 + 32, 112 + 16))
    barn.paste(darkness, box=(64, 96), mask=darkness)
    barn.paste(door, box=(64, 88), mask=door)
    barn.save(os.path.join(base_path, 'farm', 'buildings', 'Big Barn.png'))

    # Deluxe
    assets = Image.open(os.path.join(src_directory, 'Buildings', 'Deluxe Barn.png'))

    barn = assets.crop((0, 0, 112, 112))
    door = assets.crop((0, 112, 32, 112 + 16))
    darkness = assets.crop((32, 112, 32 + 32, 112 + 16))
    barn.paste(darkness, box=(64, 96), mask=darkness)
    barn.save(os.path.join(base_path, 'farm', 'buildings', 'Deluxe Barn.png'))

    # Coops

    # Normal
    assets = Image.open(os.path.join(src_directory, 'Buildings', 'Coop.png'))

    coop = assets.crop((0, 0, 96, 112))
    door = assets.crop((0, 112, 16, 112 + 16))
    coop.paste(door, box=(3, 96), mask=door)
    coop.save(os.path.join(base_path, 'farm', 'buildings', 'Coop.png'))

    # Big
    assets = Image.open(os.path.join(src_directory, 'Buildings', 'Big Coop.png'))

    coop = assets.crop((0, 0, 96, 112))
    door = assets.crop((0, 112, 16, 112 + 16))
    coop.paste(door, box=(32, 96), mask=door)
    coop.save(os.path.join(base_path, 'farm', 'buildings', 'Big Coop.png'))

    # Delux
    assets = Image.open(os.path.join(src_directory, 'Buildings', 'Deluxe Coop.png'))

    coop = assets.crop((0, 0, 96, 112))
    door = assets.crop((0, 112, 16, 112 + 16))
    coop.paste(door, box=(32, 96), mask=door)
    coop.save(os.path.join(base_path, 'farm', 'buildings', 'Deluxe Coop.png'))

    # Copy Bin Lid
    asset = Image.open(os.path.join(src_directory, 'loosesprites', 'cursors.png'))
    x = 132
    y = 235
    bin_lid = asset.crop((x, y, x+ 32, y + 16))
    bin_lid.save(os.path.join(base_path, 'farm', 'looseSprites', 'binLid.png'))