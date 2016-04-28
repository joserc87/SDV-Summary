#! /usr/bin/env python

from PIL import Image
from PIL.ImageChops import offset
from PIL.ImageOps import grayscale, colorize
import colorsys


# Apply colour to image
def tintImage(img, tint):
    i = colorize(grayscale(img), (0, 0, 0), tint)
    i.putalpha(img.split()[3])
    return i


# Takes Spritesheet and returns 16x32 image of required part
def cropImage(imageFile, index, count, dim, loc=(0, 0)):
    x = (index % count) * dim[0]
    y = (index // count) * dim[1]
    part = offset(imageFile, -x, -y).crop((0, 0, dim[0], dim[1]))
    whole_img = Image.new("RGBA", (16, 32), (0, 0, 0, 0))
    whole_img.paste(part, loc, part)
    return whole_img


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

    hair = cropImage(assets['hair'], int(player['hair']), 8, (16, 32))
    hair_color = tuple(map(int, player['hairstyleColor']))
    hair = tintImage(hair, hair_color)

    acc = cropImage(assets['accessories'], int(player['accessory']), 8, (16, 16), (0, 1))
    if int(player['accessory']) <= 5:
        acc = tintImage(acc, hair_color)

    shirt = cropImage(assets['shirts'], int(player['shirt']), 16, (8, 8), (4, 14))

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
