from PIL import Image
from PIL.ImageChops import offset
from generateAvatar import tintImage
from playerInfo import player
from farmInfo import getFarmInfo
from itertools import chain
from collections import namedtuple

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


def getPlant(img, location, colour, defaultSize=(4, 4), objectSize=(4, 4)):
    if location < 5:
        return cropImg(img, location, defaultSize, objectSize)
    else:
        plant_body = cropImg(img, 5, defaultSize, objectSize)
        plant_head = cropImg(img, 6, defaultSize, objectSize)
        plant_head = tintImage(plant_head, colour)
        plant_body.paste(plant_head, (0, 0), plant_head)
        return plant_body


def generateFarm(season, farm):
    sprite = namedtuple('Sprite', ['name', 'x', 'y', 'w', 'h', 'index', 'type', 'growth', 'flipped', 'orientation'])
    cache = {}
    craftable_blacklist = ['Twig', 'Torch', 'Sprinkler',
                           'Quality Sprinkler', 'Iridium Sprinkler']
    print('\tLoading Base...')
    farm_base = Image.open('./assets/bases/{0}_base.png'.format(season))

    print('\tLoading Spritesheets...')
    object_spritesheet = Image.open('./assets/farm/objects.png')
    craftable_spritesheet = Image.open('./assets/farm/craftables.png')
    farm['overlays'] = [sprite('overlay', 0, 14, 0, 0, 0, 1, 0, 0, 0), sprite('overlay', 0, 23, 0, 0, 0, 2, 0, 0, 0),
                                sprite('overlay', 0, 63, 0, 0, 0, 3, 0, 0, 0)]
    farm = sorted(chain.from_iterable(farm.values()), key=lambda x: x.y)
    floor_types = ['Flooring', 'HoeDirt']
    floor = [i for i in farm if i.name in floor_types]
    gates = []
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
                                   (32, 8), (32, 8))
            if item.orientation is None:
                crop_img = cropImg(crop_sprites, item.growth,
                                   (4, 8), (4, 8))
            else:
                crop_img = getPlant(crop_sprites, item.growth, item.orientation, (4, 8), (4, 8))
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
            try:
                offsetx = 0
                offsety = 0
                fence_sheet = Image.open('./assets/farm/Fence{0}.png'.format(item.type))
                if item.orientation == 12 and item.growth:
                    gates.append(item)
                    continue
                elif item.orientation == 15 and item.growth:
                    fence_img = cropImg(fence_sheet, item.orientation,
                                        defaultSize=(4, 8), objectSize=(2, 8))
                    offsetx = 5
                    offsety = 22
                else:
                    fence_img = cropImg(fence_sheet, item.orientation,
                                        defaultSize=(4, 8), objectSize=(4, 8))
                offsety = 16
                farm_base.paste(fence_img, (item.x * 16 + offsetx, item.y * 16 - offsety), fence_img)
            except Exception as e:
                print(e)

        if item.name == 'ResourceClump':
            obj_img = cropImg(object_spritesheet, item.type, objectSize=(8, 8))
            farm_base.paste(obj_img, (item.x*16, item.y*16), obj_img)

        if item.name == 'Tree':
            try:
                if item.type == 7:
                    filename = "mushroom_tree"
                else:
                    filename = "tree{0}_{1}".format(item.type, season)

                with Image.open('./assets/farm/trees/{0}.png'.format(filename)) as tree_img:
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

        if item.name == 'overlay':
            try:
                overlay_img = Image.open('./assets/bases/{0}_overlay_{1}.png'.format(season, item.type))
                farm_base.paste(overlay_img, (0, 0), overlay_img)
            except Exception as e:
                print(e)

    for item in gates:
        try:
                offsetx = 0
                offsety = 0
                fence_sheet = Image.open('./assets/farm/Fence{0}.png'.format(item.type))
                fence_img = cropImg(fence_sheet, item.orientation,
                                    defaultSize=(4, 8), objectSize=(6, 8))
                offsetx = -4
                offsety = 16
                farm_base.paste(fence_img, (item.x * 16 + offsetx, item.y * 16 - offsety), fence_img)
        except Exception as e:
                print(e)

    farm_base = farm_base.convert('RGBA').convert('P', palette=Image.ADAPTIVE, colors=255)
    return farm_base


def main():
    f = 'Vejur_118036516'
    import time
    # for f in os.listdir(os.getcwd()+'/saves/'):
    print(f)
    p = player('./saves/'+f).getPlayerInfo()['currentSeason']
    start_time = time.time()
    im = generateFarm(p, getFarmInfo('./saves/'+f))
    print('\timage generation took', time.time()-start_time)
    im.save('./farmRenders/' + f + '.png', compress_level=9)
    print('\ttotal time was', time.time()-start_time)

if __name__ == '__main__':
    main()
