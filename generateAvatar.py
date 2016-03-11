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

def cropImage(fileName, index, count, width, height):
	with Image.open(fileName) as img:
		x = (index % count) * width
		y = (index // count) * height
		return offset(img, -x, -y).crop((0,0,width,height))

def generateAvatar(player):

	gender = ''
	if player['isMale']:
		gender = 'male'
	else:
		gender = 'female'

	base = Image.open('./assets/{0}_base.png'.format(gender))
	boots = Image.open('./assets/{0}_boots.png'.format(gender))
	legs = Image.open('./assets/{0}_legs.png'.format(gender))
	hats = Image.open('./assets/hats.png')

	leg_colour = (int(player['pantsColor'][0]), int(player['pantsColor'][1]), int(player['pantsColor'][2]))
	legs = tintImage(legs, leg_colour)

	hair = cropImage('./assets/hair.png', int(player['hair']), 8, 16, 32)
	hair_color = tuple(map(int, player['hairstyleColor']))
	hair = tintImage(hair, hair_color)

	acc = cropImage('./assets/accessories.png',int(player['accessory']), 8, 16, 16) 
	if int(player['accessory']) <= 5:
		acc = tintImage(acc, hair_color)

	shirt = cropImage('./assets/shirts.png', int(player['shirt']), 16, 8,8)

	body = base.load()
	eyeColor = tuple(map(int, player['newEyeColor']))
	if player['isMale']:
		body[6,10] = eyeColor
		body[9, 10] = eyeColor
		body[6,11] = eyeColor
		body[9, 11] = eyeColor
	else:
		body[6,11] = eyeColor
		body[9, 11] = eyeColor
		body[6,12] = eyeColor
		body[9, 12] = eyeColor

	base.paste(legs, (0,-1), legs)
	base.paste(shirt, (4,14), shirt)
	base.paste(acc, (0,1), acc)
	base.paste(boots, (0,2), boots)
	base.paste(hair, (0,0), hair)
	return base

def main():
	from playerInfo import playerInfo
	# player = playerInfo('./save/Crono_116230451')
	player = playerInfo('./save/Sketchy_116441313')
	generateAvatar(player).save('test.png')

if __name__ == '__main__':
	main()