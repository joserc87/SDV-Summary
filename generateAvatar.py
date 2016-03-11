#! /usr/bin/env python

from playerInfo import playerInfo
from PIL import Image, ImageChops
from PIL.ImageOps import grayscale, colorize
import colorsys

# Apply colour to image
def tintImage(img, tint):
	i = colorize(grayscale(img), (0,0,0), tint)
	i.putalpha(img.split()[3])
	return i

def generateAvatar(player):

	base = Image.open('./assets/male_base.png')
	shoes = Image.open('./assets/male_shoes.png')
	shirts = Image.open('./assets/shirts.png')
	hairs = Image.open('./assets/hair.png')
	legs = Image.open('./assets/male_legs.png')

	leg_colour = (int(player['pantsColor'][0]), int(player['pantsColor'][1]), int(player['pantsColor'][2]))
	legs = tintImage(legs, leg_colour)


	hair_color = (int(player['hairstyleColor'][0]), int(player['hairstyleColor'][1]), int(player['hairstyleColor'][2]))
	hair_index = int(player['hair'])
	x = (hair_index % 8) * 16
	y = (hair_index // 8) * 32
	hair = ImageChops.offset(hairs, -x, -y).crop((0,0,16,32))
	hair = tintImage(hair, hair_color)

	shirt_index = int(player['shirt'])
	x = (shirt_index % 16) * 8
	y = (shirt_index // 16) * 8
	shirt = ImageChops.offset(shirts, -x, -y).crop((0,0,8,8))

	base.paste(hair, (0,-1), hair)
	base.paste(legs, (0,0), legs)
	base.paste(shirt, (4,13), shirt)
	base.paste(shoes, (0,2), shoes)
	base.save('test.png')

def main():
	player = playerInfo('./save/Crono_116230451')
	# player = playerInfo('./save/Sketchy_116441313')
	generateAvatar(player)

if __name__ == '__main__':
	main()