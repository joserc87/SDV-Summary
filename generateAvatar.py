#! /usr/bin/env python

from PIL import Image
from PIL.ImageChops import offset
from PIL.ImageOps import grayscale, colorize
import colorsys

# Apply colour to image
def tintImage(img, tint):
	i = colorize(grayscale(img), (0,0,0), tint)
	i.putalpha(img.split()[3])
	return i

# Takes Spritesheet and returns 16x32 image of required part
def cropImage(fileName, index, count, dim, loc = (0,0)):
	with Image.open(fileName) as img:
		x = (index % count) * dim[0]
		y = (index // count) * dim[1]
		part = offset(img, -x, -y).crop((0,0,dim[0],dim[1]))
	whole_img = Image.new("RGBA", (16,32), (0,0,0,0))
	whole_img.paste(part, loc, part)
	return whole_img

def generateAvatar(player):

	gender = ''
	if player['isMale'] == 'true':
		gender = 'male'
	else:
		gender = 'female'

	base = Image.open('./assets/{0}_base.png'.format(gender))
	boots = Image.open('./assets/{0}_boots.png'.format(gender))
	legs = Image.open('./assets/{0}_legs.png'.format(gender))
	hats = Image.open('./assets/hats.png')

	leg_colour = (int(player['pantsColor'][0]), int(player['pantsColor'][1]), int(player['pantsColor'][2]))
	legs = tintImage(legs, leg_colour)

	hair = cropImage('./assets/hair.png', int(player['hair']), 8, (16, 32))
	hair_color = tuple(map(int, player['hairstyleColor']))
	hair = tintImage(hair, hair_color)

	acc = cropImage('./assets/accessories.png',int(player['accessory']), 8, (16, 16), (0, 1)) 
	if int(player['accessory']) <= 5:
		acc = tintImage(acc, hair_color)

	shirt = cropImage('./assets/shirts.png', int(player['shirt']), 16, (8,8), (4, 14))

	skin_x = int(player['skin']) % 24 * 1
	skin_y = int(player['skin']) // 24 * 1
	skin_color = Image.open('./assets/skinColors.png').getpixel((skin_x,skin_y))
	base = tintImage(base, skin_color)

	body = base.load()
	eyeColor = tuple(map(int, player['newEyeColor']))
	white = (255,255,255)
	if player['isMale'] == 'true':
		body[6,10] = eyeColor
		body[9, 10] = eyeColor
		body[6,11] = eyeColor
		body[9, 11] = eyeColor
		body[5,10] = white
		body[10, 10] = white
		body[5,11] = white
		body[10, 11] = white
	else:
		body[6,11] = eyeColor
		body[9, 11] = eyeColor
		body[6,12] = eyeColor
		body[9, 12] = eyeColor
		body[5,11] = white
		body[10, 11] = white
		body[5,12] = white
		body[10, 12] = white

	base = Image.alpha_composite(base, legs)
	base = Image.alpha_composite(base, shirt)
	base = Image.alpha_composite(base, acc)
	base = Image.alpha_composite(base, boots)
	base = Image.alpha_composite(base, hair)
	return base

def main():
	from playerInfo import playerInfo
	# player = playerInfo('./save/Crono_116230451')
	player = playerInfo('./save/Sketchy_116441313')
	generateAvatar(player).save('test.png')

if __name__ == '__main__':
	main()