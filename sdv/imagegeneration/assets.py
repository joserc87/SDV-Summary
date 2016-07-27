import os

from PIL import Image
from sdv import app

asset_dir = app.config.get('ASSET_PATH')


def loadFarmAssets():
    assets = {
                'base': {
                            'spring': Image.open(os.path.join(asset_dir, 'bases', 'spring_base.png')),
                            'summer': Image.open(os.path.join(asset_dir, 'bases', 'summer_base.png')),
                            'fall': Image.open(os.path.join(asset_dir, 'bases', 'fall_base.png')),
                            'winter': Image.open(os.path.join(asset_dir, 'bases', 'winter_base.png'))
                          },
                'overlays': {
                                'spring': [
                                                Image.open(os.path.join(asset_dir, 'bases', 'spring_overlay_0.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'spring_overlay_1.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'spring_overlay_2.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'spring_overlay_3.png'))
                                            ],
                                'summer': [
                                                Image.open(os.path.join(asset_dir, 'bases', 'summer_overlay_0.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'summer_overlay_1.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'summer_overlay_2.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'summer_overlay_3.png'))
                                            ],
                                'fall': [
                                                Image.open(os.path.join(asset_dir, 'bases', 'fall_overlay_0.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'fall_overlay_1.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'fall_overlay_2.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'fall_overlay_3.png'))
                                            ],
                                'winter': [
                                                Image.open(os.path.join(asset_dir, 'bases', 'winter_overlay_0.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'winter_overlay_1.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'winter_overlay_2.png')),
                                                Image.open(os.path.join(asset_dir, 'bases', 'winter_overlay_3.png'))
                                            ]
                               },
                'objects': Image.open(os.path.join(asset_dir, 'farm', 'objects.png')),
                'craftables': Image.open(os.path.join(asset_dir, 'farm', 'craftables.png')),
                'flooring': Image.open(os.path.join(asset_dir, 'farm', 'flooring.png')),
                'hoe dirt': {
                              'normal': Image.open(os.path.join(asset_dir, 'farm', 'hoeDirt.png')),
                              'winter': Image.open(os.path.join(asset_dir, 'farm', 'hoeDirtsnow.png'))
                              },
                'crops': Image.open(os.path.join(asset_dir, 'farm', 'crops.png')),
                'fences': {
                                'wood': Image.open(os.path.join(asset_dir, 'farm', 'Fence1.png')),
                                'stone': Image.open(os.path.join(asset_dir, 'farm', 'Fence2.png')),
                                'iron': Image.open(os.path.join(asset_dir, 'farm', 'Fence3.png')),
                                'hardwood': Image.open(os.path.join(asset_dir, 'farm', 'Fence5.png'))
                            },
                'trees': {
                            'oak': {
                                        'spring': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree1_spring.png')),
                                        'summer': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree1_summer.png')),
                                        'fall': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree1_fall.png')),
                                        'winter': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree1_winter.png'))
                                    },
                            'maple': {
                                        'spring': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree2_spring.png')),
                                        'summer': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree2_summer.png')),
                                        'fall': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree2_fall.png')),
                                        'winter': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree2_winter.png'))
                                        },
                            'pine': {
                                        'spring': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree3_spring.png')),
                                        'summer': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree3_summer.png')),
                                        'fall': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree3_fall.png')),
                                        'winter': Image.open(os.path.join(asset_dir, 'farm', 'trees/tree3_winter.png'))
                                     },
                            'mushroom': Image.open(os.path.join(asset_dir, 'farm', 'trees/mushroom_tree.png')),
                            'fruit': Image.open(os.path.join(asset_dir, 'farm', 'fruitTrees.png'))
                            },
                'grass': Image.open(os.path.join(asset_dir, 'farm', 'grass/grass.png')),
                'buildings': {
                                    'barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Barn.png')),
                                    'big barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Big Barn.png')),
                                    'deluxe barn': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Deluxe Barn.png')),
                                    'coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Coop.png')),
                                    'big coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Big Coop.png')),
                                    'deluxe coop': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Deluxe Coop.png')),
                                    'greenhouse': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Greenhouse.png')),
                                    'house': Image.open(os.path.join(asset_dir, 'farm', 'buildings/houses.png')),
                                    'silo': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Silo.png')),
                                    'slime hutch': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Slime Hutch.png')),
                                    'stable': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Stable.png')),
                                    'well': Image.open(os.path.join(asset_dir, 'farm', 'buildings/Well.png'))
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