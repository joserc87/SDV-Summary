import os

from PIL import Image
from sdv import app

asset_dir = app.config.get('ASSET_PATH')

overlays = [
    'Buildings.png',
    'Front.png',
    'AlwaysFront.png'
]


def loadFarmAssets():
    assets = {
                'base': {
                    'Defaut': {
                        'spring': Image.open(os.path.join(asset_dir, 'base', 'Default', 'spring', 'Back.png')),
                        'summer': Image.open(os.path.join(asset_dir, 'base', 'Default', 'summer', 'Back.png')),
                        'fall': Image.open(os.path.join(asset_dir, 'base', 'Default', 'fall', 'Back.png')),
                        'winter': Image.open(os.path.join(asset_dir, 'base', 'Default', 'winter', 'Back.png'))
                    },
                    'Combat': {
                        'spring': Image.open(os.path.join(asset_dir, 'base', 'Combat', 'spring', 'Back.png')),
                        'summer': Image.open(os.path.join(asset_dir, 'base', 'Combat', 'summer', 'Back.png')),
                        'fall': Image.open(os.path.join(asset_dir, 'base', 'Combat', 'fall', 'Back.png')),
                        'winter': Image.open(os.path.join(asset_dir, 'base', 'Combat', 'winter', 'Back.png'))
                    },
                    'Fishing': {
                        'spring': Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'spring', 'Back.png')),
                        'summer': Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'summer', 'Back.png')),
                        'fall': Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'fall', 'Back.png')),
                        'winter': Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'winter', 'Back.png'))
                    },
                    'Mining': {
                        'spring': Image.open(os.path.join(asset_dir, 'base', 'Mining', 'spring', 'Back.png')),
                        'summer': Image.open(os.path.join(asset_dir, 'base', 'Mining', 'summer', 'Back.png')),
                        'fall': Image.open(os.path.join(asset_dir, 'base', 'Mining', 'fall', 'Back.png')),
                        'winter': Image.open(os.path.join(asset_dir, 'base', 'Mining', 'winter', 'Back.png'))
                    },
                    'Foraging': {
                        'spring': Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'spring', 'Back.png')),
                        'summer': Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'summer', 'Back.png')),
                        'fall': Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'fall', 'Back.png')),
                        'winter': Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'winter', 'Back.png'))
                    }
                },
                'overlays': {
                    'Defaut': {
                        'spring': [Image.open(os.path.join(asset_dir, 'base', 'Default', 'spring', s)) for s in overlays],
                        'summer': [Image.open(os.path.join(asset_dir, 'base', 'Default', 'summer', s)) for s in overlays ],
                        'fall': [Image.open(os.path.join(asset_dir, 'base', 'Default', 'fall', s)) for s in overlays],
                        'winter': [Image.open(os.path.join(asset_dir, 'base', 'Default', 'winter', s)) for s in overlays]
                    },
                    'Combat': {
                        'spring': [Image.open(os.path.join(asset_dir, 'base', 'Combat', 'spring', s)) for s in overlays],
                        'summer': [Image.open(os.path.join(asset_dir, 'base', 'Combat', 'summer', s)) for s in overlays],
                        'fall': [Image.open(os.path.join(asset_dir, 'base', 'Combat', 'fall', s)) for s in overlays],
                        'winter': [Image.open(os.path.join(asset_dir, 'base', 'Combat', 'winter', s)) for s in overlays]
                    },
                    'Fishing': {
                        'spring': [Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'spring', s)) for s in overlays],
                        'summer': [Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'summer', s)) for s in overlays],
                        'fall': [Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'fall', s)) for s in overlays],
                        'winter': [Image.open(os.path.join(asset_dir, 'base', 'Fishing', 'winter', s)) for s in overlays]
                    },
                    'Mining': {
                        'spring': [Image.open(os.path.join(asset_dir, 'base', 'Mining', 'spring', s)) for s in overlays],
                        'summer': [Image.open(os.path.join(asset_dir, 'base', 'Mining', 'summer', s)) for s in overlays],
                        'fall': [Image.open(os.path.join(asset_dir, 'base', 'Mining', 'fall', s)) for s in overlays],
                        'winter': [Image.open(os.path.join(asset_dir, 'base', 'Mining', 'winter', s)) for s in overlays]
                    },
                    'Foraging': {
                        'spring': [Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'spring', s)) for s in overlays],
                        'summer': [Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'summer', s)) for s in overlays],
                        'fall': [Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'fall', s)) for s in overlays],
                        'winter': [Image.open(os.path.join(asset_dir, 'base', 'Foraging', 'winter', s)) for s in overlays]
                    }
                },
                'objects': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'springobjects.png')),
                'craftables': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'craftables.png')),
                'flooring': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'flooring.png')),
                'hoe dirt': {
                              'normal': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'hoeDirt.png')),
                              'winter': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'hoeDirtsnow.png'))
                              },
                'crops': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'crops.png')),
                'fences': {
                                'wood': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence1.png')),
                                'stone': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence2.png')),
                                'iron': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence3.png')),
                                'hardwood': Image.open(os.path.join(asset_dir, 'farm', 'looseSprites', 'Fence5.png'))
                            },
                'trees': {
                            'oak': {
                                        'spring': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_spring.png')),
                                        'summer': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_summer.png')),
                                        'fall': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_fall.png')),
                                        'winter': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree1_winter.png'))
                                    },
                            'maple': {
                                        'spring': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_spring.png')),
                                        'summer': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_summer.png')),
                                        'fall': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_fall.png')),
                                        'winter': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree2_winter.png'))
                                        },
                            'pine': {
                                        'spring': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_spring.png')),
                                        'summer': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_spring.png')),
                                        'fall': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_fall.png')),
                                        'winter': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'tree3_winter.png'))
                                     },
                            'mushroom': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'mushroom_tree.png')),
                            'fruit': Image.open(os.path.join(asset_dir, 'farm', 'tileSheets', 'fruitTrees.png'))
                            },
                'grass': Image.open(os.path.join(asset_dir, 'farm', 'terrainFeatures', 'grass.png')),
                'buildings': {
                                    'barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Barn.png')),
                                    'big barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Big Barn.png')),
                                    'deluxe barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Deluxe Barn.png')),
                                    'coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Coop.png')),
                                    'big coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Big Coop.png')),
                                    'deluxe coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Deluxe Coop.png')),
                                    'greenhouse': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Houses.png')),
                                    'house': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Houses.png')),
                                    'silo': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Silo.png')),
                                    'slime hutch': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Slime Hutch.png')),
                                    'stable': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Stable.png')),
                                    'well': Image.open(os.path.join(asset_dir, 'farm', 'buildings', 'Well.png'))
                                }
              }

    return assets

def loadAvatarAssets():
    assets = {
                'base': {
                            'male': Image.open(os.path.join(asset_dir, 'player', 'male_base.png')),
                            'female': Image.open(os.path.join(asset_dir, 'player', 'female_base.png'))
                          },
                'boots': {
                            'male': Image.open(os.path.join(asset_dir, 'player', 'male_boots.png')),
                            'female': Image.open(os.path.join(asset_dir, 'player', 'female_boots.png'))
                           },
                'legs': {
                            'male': Image.open(os.path.join(asset_dir, 'player', 'male_legs.png')),
                            'female': Image.open(os.path.join(asset_dir, 'player', 'female_legs.png'))
                          },
                'arms': {
                            'male': Image.open(os.path.join(asset_dir, 'player', 'male_arms.png')),
                            'female': Image.open(os.path.join(asset_dir, 'player', 'female_arms.png'))
                          },
                'hair': Image.open(os.path.join(asset_dir, 'player', 'hair.png')),
                'accessories': Image.open(os.path.join(asset_dir, 'player', 'accessories.png')),
                'shirts': Image.open(os.path.join(asset_dir, 'player', 'shirts.png')),
                'skin colors': Image.open(os.path.join(asset_dir, 'player', 'skinColors.png'))
               }

    return assets