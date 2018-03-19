import os

from PIL import Image
from sdv import app

asset_dir = app.config.get('ASSET_PATH')

overlay_layers = {
    'Front',
    'AlwaysFront',
    'Buildings'
}


def open_nicely(filename):
    im = Image.open(filename)
    im.load()
    return im


def load_overlays(season, base):
    overlays = dict()

    for layer in overlay_layers:
        overlays[layer] = list()
        overlay_path = os.path.join(asset_dir, 'base', base, season, layer)
        for i in range(65):
            overlays[layer].append(
                    open_nicely(os.path.join(overlay_path, '{}-{}.png'.format(layer, i))))
    return overlays


def loadFarmAssets(season='spring', base='Default'):
    assets = {
        'base': {
            base: {season: Image.open(os.path.join(asset_dir, 'base', base, season, 'Back.png'))}
        },
        'overlays': {
            base: {season: load_overlays(season, base)}
        },
        'objects': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'springobjects.png')),
        'craftables': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'Craftables.png')),
        'flooring': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'flooring.png')),
        'hoe dirt': {
            'normal': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'hoeDirt.png')),
            'winter': Image.open(
                    os.path.join(asset_dir, 'farm', 'terrainFeatures', 'hoeDirtsnow.png'))
        },
        'crops': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'crops.png')),
        'fences': {
            'wood': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence1.png')),
            'stone': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence2.png')),
            'iron': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence3.png')),
            'hardwood': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence5.png'))
        },
        'bushes': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'bushes.png')),
        'trees': {
            'oak': {
                'spring': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_spring.png')),
                'summer': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_summer.png')),
                'fall': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_fall.png')),
                'winter': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_winter.png'))
            },
            'maple': {
                'spring': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_spring.png')),
                'summer': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_summer.png')),
                'fall': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_fall.png')),
                'winter': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_winter.png'))
            },
            'pine': {
                'spring': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_spring.png')),
                'summer': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_spring.png')),
                'fall': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_fall.png')),
                'winter': Image.open(
                        os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_winter.png'))
            },
            'mushroom': Image.open(
                    os.path.join(asset_dir, 'farm', 'terrainFeatures', 'mushroom_tree.png')),
            'fruit': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'fruitTrees.png'))
        },
        'grass': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'grass.png')),
        'buildings': {
            'barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Barn.png')),
            'big barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Big Barn.png')),
            'deluxe barn': Image.open(
                    os.path.join(asset_dir, 'farm', 'buildings', 'Deluxe Barn.png')),
            'coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Coop.png')),
            'big coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Big Coop.png')),
            'deluxe coop': Image.open(
                    os.path.join(asset_dir, 'farm', 'buildings', 'Deluxe Coop.png')),
            'greenhouse': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'houses.png'))
                .crop((160, 0, 160 + 112, 144 * 3)),
            'house': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'houses.png'))
                .crop((0, 0, 160, 144 * 3)),
            'silo': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Silo.png')),
            'slime hutch': Image.open(
                    os.path.join(asset_dir, 'farm', 'buildings', 'Slime Hutch.png')),
            'stable': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Stable.png')),
            'well': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Well.png')),
            'earth obelisk': Image.open(
                    os.path.join(asset_dir, 'farm', 'buildings', 'Earth Obelisk.png')),
            'gold clock': Image.open(
                    os.path.join(asset_dir, 'farm', 'buildings', 'Gold Clock.png')),
            'junimo hut': {
                'spring': Image.open(
                        os.path.join(asset_dir, 'farm', 'buildings', 'Junimo Hut.png')).crop(
                        (0, 0, 48, 64)),
                'summer': Image.open(
                        os.path.join(asset_dir, 'farm', 'buildings', 'Junimo Hut.png')).crop(
                        (48, 0, 48 * 2, 64)),
                'fall': Image.open(
                        os.path.join(asset_dir, 'farm', 'buildings', 'Junimo Hut.png')).crop(
                        (48 * 2, 0, 48 * 3, 64)),
                'winter': Image.open(
                        os.path.join(asset_dir, 'farm', 'buildings', 'Junimo Hut.png')).crop(
                        (48 * 3, 0, 48 * 4, 64))
            },
            'mill': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Mill.png')),
            'shed': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Shed.png')),
            'water obelisk': Image.open(
                    os.path.join(asset_dir, 'farm', 'buildings', 'Water Obelisk.png'))
        },
        'binLid': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'binLid.png'))
    }
    return assets


def loadAvatarAssets():
    assets = {
        'base': {
            'male': Image.open(os.path.join(asset_dir, 'player', 'male', 'male_base.png')),
            'female': Image.open(os.path.join(asset_dir, 'player', 'female', 'female_base.png'))
        },
        'boots': {
            'male': Image.open(os.path.join(asset_dir, 'player', 'male', 'male_boots.png')),
            'female': Image.open(os.path.join(asset_dir, 'player', 'female', 'female_boots.png'))
        },
        'legs': {
            'male': Image.open(os.path.join(asset_dir, 'player', 'male', 'male_legs.png')),
            'female': Image.open(os.path.join(asset_dir, 'player', 'female', 'female_legs.png'))
        },
        'arms': {
            'male': Image.open(os.path.join(asset_dir, 'player', 'male', 'male_arms.png')),
            'female': Image.open(os.path.join(asset_dir, 'player', 'female', 'female_arms.png'))
        },
        'hair': Image.open(os.path.join(asset_dir, 'player', 'misc', 'hairstyles.png')),
        'accessories': Image.open(os.path.join(asset_dir, 'player', 'misc', 'accessories.png')),
        'shirts': Image.open(os.path.join(asset_dir, 'player', 'misc', 'shirts.png')),
        'skin colors': Image.open(os.path.join(asset_dir, 'player', 'misc', 'skinColors.png'))
    }

    return assets
