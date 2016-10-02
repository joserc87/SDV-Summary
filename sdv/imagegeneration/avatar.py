#! /usr/bin/env python

from PIL import Image
from .tools import tintImage, cropImg
from . assets import loadAvatarAssets


def generateAvatar(player, assets=None):
    if player['isMale'] == 'true':
        gender = 'male'
    else:
        gender = 'female'

    if assets is None:
        assets = loadAvatarAssets()

    base = assets['base'][gender]

    leg_colour = (int(player['pantsColor'][0]), int(player['pantsColor'][1]), int(player['pantsColor'][2]))
    legs = tintImage(assets['legs'][gender], leg_colour)

    hair = cropImg(assets['hair'], int(player['hair']), defaultSize=(16, 32*3), objectSize=(16, 32), resize=True, displacement=(0, 0))
    hair_color = tuple(map(int, player['hairstyleColor']))
    hair = tintImage(hair, hair_color)

    acc = cropImg(assets['accessories'], int(player['accessory']), objectSize=(16, 16*2), resize=True, displacement=(0, 1))
    if int(player['accessory']) <= 5:
        acc = tintImage(acc, hair_color)

    shirt = cropImg(assets['shirts'], int(player['shirt']), defaultSize=(8, 8*4), objectSize=(8, 8), resize=True, displacement=(4, 14))

    skin_x = int(player['skin']) % 24 * 1
    skin_y = int(player['skin']) // 24 * 1
    skin_color = assets['skin colors'].getpixel((skin_x, skin_y))
    base = tintImage(base, skin_color)
    arms = tintImage(assets['arms'][gender], skin_color)

    body = base.load()
    eyeColor = tuple(map(int, player['newEyeColor']))
    white = (255, 255, 255)
    if player['isMale'] == 'true':
        body[6, 10] = eyeColor
        body[9, 10] = eyeColor
        body[6, 11] = eyeColor
        body[9, 11] = eyeColor
        body[5, 10] = white
        body[10, 10] = white
        body[5, 11] = white
        body[10, 11] = white
    else:
        body[6, 11] = eyeColor
        body[9, 11] = eyeColor
        body[6, 12] = eyeColor
        body[9, 12] = eyeColor
        body[5, 11] = white
        body[10, 11] = white
        body[5, 12] = white
        body[10, 12] = white

    base = Image.alpha_composite(base, hair)
    base = Image.alpha_composite(base, arms)
    base = Image.alpha_composite(base, legs)
    base = Image.alpha_composite(base, shirt)
    base = Image.alpha_composite(base, acc)
    base = Image.alpha_composite(base, assets['boots'][gender])
    return base
