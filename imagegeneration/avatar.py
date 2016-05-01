#! /usr/bin/env python

from PIL import Image
from .tools import tintImage, cropImg


def loadAvatarAssets():
    assets = {
                'base': {
                            'male': Image.open('./assets/player/male_base.png'),
                            'female': Image.open('./assets/player/female_base.png')
                          },
                'boots': {
                            'male': Image.open('./assets/player/male_boots.png'),
                            'female': Image.open('./assets/player/female_boots.png')
                           },
                'legs': {
                            'male': Image.open('./assets/player/male_legs.png'),
                            'female': Image.open('./assets/player/female_legs.png')
                          },
                'arms': {
                            'male': Image.open('./assets/player/male_arms.png'),
                            'female': Image.open('./assets/player/female_arms.png')
                          },
                'hair': Image.open('./assets/player/hair.png'),
                'accessories': Image.open('./assets/player/accessories.png'),
                'shirts': Image.open('./assets/player/shirts.png'),
                'skin colors': Image.open('./assets/player/skinColors.png')
               }

    return assets


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

    hair = cropImg(assets['hair'], int(player['hair']), defaultSize=(16, 32), objectSize=(16,32), resize=True)
    hair_color = tuple(map(int, player['hairstyleColor']))
    hair = tintImage(hair, hair_color)

    acc = cropImg(assets['accessories'], int(player['accessory']), resize=True)
    if int(player['accessory']) <= 5:
        acc = tintImage(acc, hair_color)

    shirt = cropImg(assets['shirts'], int(player['shirt']), defaultSize=(8, 8), objectSize=(8, 8), resize=True)

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
    base = Image.alpha_composite(base, acc)
    base = Image.alpha_composite(base, arms)
    base = Image.alpha_composite(base, legs)
    base = Image.alpha_composite(base, shirt)
    base = Image.alpha_composite(base, assets['boots'][gender])
    return base


def main():
    from playerInfo import playerInfo
    # player = playerInfo('./save/Crono_116230451')
    player = playerInfo('./saves/Sketchy_116441313')
    generateAvatar(player).save('test.png')

if __name__ == '__main__':
    main()
