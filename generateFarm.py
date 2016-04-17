from PIL import Image
from PIL.ImageChops import offset
from playerInfo import player
from farmInfo import getFarmInfo
from itertools import chain

import os
import random


def cropImg(img, location, defaultSize=(4, 4), objectSize=(4, 4)):
    row = int(img.width / (4*defaultSize[0]))
    x = (location % row) * 4 * defaultSize[0]
    y = (location // row) * 4 * defaultSize[1]
    return offset(img, -x, -y).crop((0, 0, 4*objectSize[0], 4*objectSize[1]))


def loadTree(ss_tree, loc=0):
    tree = Image.new('RGBA', (3*16, 6*16))
    body = cropImg(ss_tree, loc, objectSize=(12, 24))
    stump = cropImg(ss_tree, 20, objectSize=(4, 8))
    tree.paste(stump, (1*16, 4*16), stump)
    tree.paste(body, (0, 0), body)
    return tree


def generateFarm(player, farm):
    season = player.getCurrentSeason()
    cache = {}
    craftable_blacklist = ['Twig', 'Torch', 'Sprinkler',
                           'Quality Sprinkler', 'Iridium Sprinkler']

    print('\tLoading Base...')
    farm_base = Image.open('./assets/bases/{0}_base.png'.format(season))

    print('\tLoading Spritesheets...')
    object_spritesheet = Image.open('./assets/farm/objects.png')
    craftable_spritesheet = Image.open('./assets/farm/craftables.png')

    farm = sorted(chain.from_iterable(farm.values()), key=lambda x: x.y)
    floor_types = ['Flooring', 'HoeDirt']
    floor = [i for i in farm if i.name in floor_types]
    other_things = [i for i in farm if i not in floor]

    print('\tRendering Sprites...')
    for item in floor:
        if item.name == 'Flooring':
            if 'flooring-'+str(item.type) in cache:
                floor_type = cache['flooring-'+str(item.type)]
            else:
                with Image.open('./assets/farm/flooring.png') as floor_sheet:
                    floor_type = cropImg(floor_sheet, item.type,
                                         (16, 16), (16, 16))
                    cache['flooring-'+str(item.type)] = floor_type
            floor_view = cropImg(floor_type, item.orientation)
            farm_base.paste(floor_view, (item.x*16, item.y*16), floor_view)

        if item.name == 'HoeDirt':
            end = ""
            if season == 'winter':
                end = "snow"
            hoe_sheet = Image.open('./assets/farm/hoeDirt' + end + '.png')
            hoe_tile = cropImg(hoe_sheet, item.orientation)
            farm_base.paste(hoe_tile, (item.x*16, item.y*16), hoe_tile)

    for item in other_things:
        if item.name == 'Flooring':
            if 'flooring-'+str(item.type) in cache:
                floor_type = cache['flooring-'+str(item.type)]
            else:
                with Image.open('./assets/farm/flooring.png') as floor_sheet:
                    floor_type = cropImg(floor_sheet, item.type,
                                         (16, 16), (16, 16))
                    cache['flooring-'+str(item.type)] = floor_type
            floor_view = cropImg(floor_type, item.orientation,
                                 objectSize=(1, 1))
            farm_base.paste(floor_view, (item.x*16, item.y*16), floor_view)

        if 'Crop' in item.name:
            crop_spritesheet = Image.open('./assets/farm/crops.png')
            crop_sprites = cropImg(crop_spritesheet, item.type,
                                   (28, 8), (28, 8))
            crop_img = cropImg(crop_sprites, item.growth,
                               (4, 8), (4, 8))
            if item.flipped:
                crop_img = crop_img.transpose(Image.FLIP_LEFT_RIGHT)
            farm_base.paste(crop_img, (item.x*16, item.y*16 - 16), crop_img)

        if item.name == 'Object':
            if item.type == "Crafting" and item.orientation not in craftable_blacklist:
                obj_img = cropImg(craftable_spritesheet, item.index,
                                  (4, 8), (4, 8))
                offset = 16
            else:
                obj_img = cropImg(object_spritesheet, item.index)
                offset = 0
            farm_base.paste(obj_img, (item.x*16, item.y*16 - offset), obj_img)

        if item.name == 'Fence':
            fence_sheet = Image.open('./assets/farm/Fence{0}.png'.format(item.type))
            fence_img = cropImg(fence_sheet, item.orientation,
                                defaultSize=(4, 8), objectSize=(4, 8))
            offset = 16
            farm_base.paste(fence_img, (item.x * 16, item.y * 16 - offset), fence_img)

        if item.name =='Gate':
            print('gate')

        if item.name == 'ResourceClump':
            obj_img = cropImg(object_spritesheet, item.type, objectSize=(8, 8))
            farm_base.paste(obj_img, (item.x*16, item.y*16), obj_img)

        if item.name == 'Tree':
            try:
                with Image.open('./assets/farm/tree{0}_{1}.png'.format(item.type, season)) as tree_img:
                    if item.growth == 0:
                        tree_crop = cropImg(tree_img, 26)
                        offsetx = 0
                        offsety = 0
                    if item.growth == 1:
                        tree_crop = cropImg(tree_img, 24)
                        offsetx = 0
                        offsety = 0
                    if item.growth == 2:
                        tree_crop = cropImg(tree_img, 25)
                        offsetx = 0
                        offsety = 0
                    if item.growth == 3 or item.growth == 4:
                        tree_crop = cropImg(tree_img, 18, objectSize=(4, 8))
                        offsetx = 0
                        offsety = 16
                    else:
                        tree_crop = loadTree(tree_img)
                        offsety = 5*16
                        offsetx = 1*16
                if item.flipped:
                    tree_crop = tree_crop.transpose(Image.FLIP_LEFT_RIGHT)
                farm_base.paste(tree_crop, (item.x*16 - offsetx, item.y*16 - offsety), tree_crop)
            except Exception as e:
                print(e)

        if item.name == 'FruitTree':
            seasons = {'spring': 0, 'summer': 1, 'fall': 2, 'winter': 3}
            try:
                with Image.open('./assets/farm/fruitTrees.png') as tree_img:
                    if item.growth <= 3:
                        tree_crop = cropImg(tree_img, item.growth + 1+9*item.type,
                                            defaultSize=(12, 0), objectSize=(12, 20))
                    else:
                        tree_crop = cropImg(tree_img, 4 + seasons[season] + 9*item.type,
                                            defaultSize=(12, 20), objectSize=(12, 20))
                    offsety = 4*16
                    offsetx = 1*16
                    if item.flipped:
                        tree_crop = tree_crop.transpose(Image.FLIP_LEFT_RIGHT)
                    farm_base.paste(tree_crop, (item.x*16 - offsetx, item.y*16 - offsety), tree_crop)
            except Exception as e:
                print(e)

        if item.name == "Building":
            try:
                building_img = Image.open('./assets/farm/buildings/{0}.png'.format(item.type))
                offsety = building_img.height - (item.h)*16
                farm_base.paste(building_img, (item.x*16, item.y*16 - offsety), building_img)
            except Exception as e:
                print(e)

        if item.name == "Grass":
            try:
                xmask = 0b01
                ymask = 0b10
                grass_spritesheet = Image.open('./assets/farm/grass/grass.png')
                s = {'spring': 0, 'summer': 4, 'fall': 8}
                for i in range(item.growth):
                    grass_img = cropImg(grass_spritesheet, s[season] + random.randint(0, 2),
                                        (4, 5), (4, 5))
                    offsety = 8 + (ymask & i)*4 - 16 + random.randint(-2, 2)
                    offsetx = 12 + (xmask & i)*8 - 16 + random.randint(-2, 2)
                    farm_base.paste(grass_img, (item.x*16 + offsetx, item.y*16 + offsety), grass_img)
            except Exception as e:
                print(e)

        if item.name == "House":
            try:
                house_ss = Image.open('./assets/farm/buildings/houses.png')
                house_img = cropImg(house_ss, item.index,
                                    defaultSize=(40, 36), objectSize=(40, 36))
                farm_base.paste(house_img, (item.x*16, item.y*16), house_img)
            except Exception as e:
                print(e)
        if item.name == "Greenhouse":
            try:
                greenhouse_ss = Image.open('./assets/farm/buildings/greenhouse.png')
                greenhouse_img = cropImg(greenhouse_ss, item.index,
                                    defaultSize=(28, 40), objectSize=(28, 40))
                farm_base.paste(greenhouse_img, (item.x*16, item.y*16), greenhouse_img)
            except Exception as e:
                print(e)
    overlay = Image.open('./assets/bases/{0}_overlay.png'.format(season))
    farm_base.paste(overlay, (0, 0), overlay)
    return farm_base


def main():
    # f = 'Crono_116230451'
    for f in os.listdir(os.getcwd()+'/saves/'):
        print(f)
        p = player('./saves/'+f)
        generateFarm(p, getFarmInfo('./saves/'+f)).save('./farmRenders/' + f + '.png')

if __name__ == '__main__':
    main()
