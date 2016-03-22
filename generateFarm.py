from PIL import Image
from PIL.ImageChops import offset
from playerInfo import player
from farmInfo import getFarmInfo

import os

def cropImg(img, location, row, w=1, h=1, m=1):
	x = (location % row) * 16
	y = (location // row) * 16 * m
	return offset(img, -x, -y).crop((0,0,w*16, h*16))

def generateFarm(player, farm):
	season = player.getCurrentSeason()
	farm_base = Image.open('./bases/{0}_base.png'.format(season))

	flooring_types = {}

	object_spritesheet = Image.open('./assets/farm/objects.png')
	craftable_spritesheet = Image.open('./assets/farm/craftables.png')

	craftable_blacklist = ['Twig', 'Torch', 'Quality Sprinkler', 'Iridium Sprinkler']

	for obj in farm['objects']:
		if obj[4] == "Crafting" and obj[0] not in craftable_blacklist:
			obj_img = cropImg(craftable_spritesheet, obj[3], 8, 1, 2, 2).resize((64,128))
			offset = 64
		else:
			obj_img = cropImg(object_spritesheet, obj[3], 24).resize((64,64))
			offset = 0

		farm_base.paste(obj_img, (obj[1]*64, obj[2]*64 - offset), obj_img)

	maxGrowth = 0
	for tFeat in farm['terrainFeatures']:
		if tFeat[0] == 'Tree':
			maxGrowth = max(maxGrowth, tFeat[4])
			try:
				with Image.open('./assets/farm/tree{0}_{1}.png'.format(tFeat[3], season)) as tree_img:
					tree_crop = cropImg(tree_img, 0, 1, 3, 6).resize((3*64,6*64))
					offsety = 5*64
					offsetx = 1 * 64

				farm_base.paste(tree_crop, (tFeat[1]*64 - offsetx, tFeat[2]*64 - offsety), tree_crop)
			except Exception as e:
				print(e)
		elif tFeat[0] == 'Flooring':
			# print(tFeat)
			if str(tFeat[3]) in flooring_types:
				floor_type = flooring_types[str(tFeat[3])]
			else:
				with Image.open('./assets/farm/flooring.png') as floor_sheet:
					floor_type = cropImg(floor_sheet, tFeat[3], 4, 64,64)
					flooring_types[str(tFeat[3])] = floor_type
			floor_view = cropImg(floor_type, tFeat[4], 4).resize((64,64))
			farm_base.paste(floor_view, (tFeat[1]*64, tFeat[2]*64), floor_view)
		# else:
			# print(tFeat)
			# 
	for rClump in farm['resourceClumps']:
		# print(rClump)
		obj_img = cropImg(object_spritesheet, rClump[0], 24, 2,2).resize((128,128))
		# obj_img.show()
		farm_base.paste(obj_img, (rClump[1]*64, rClump[2]*64), obj_img)

	return farm_base


def main():
	# f = 'Sketchy_116441313'
	for f in os.listdir(os.getcwd()+'/saves/'):
		print(f)
		p = player('./saves/'+f)
		generateFarm(p, getFarmInfo('./saves/'+f)).save('./farmRenders/' +f+'.png')

if __name__ == '__main__':
	main()