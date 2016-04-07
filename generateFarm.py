from PIL import Image
from PIL.ImageChops import offset
from playerInfo import player
from farmInfo import getFarmInfo
from itertools import chain

import os


def cropImg(img, location, defaultSize=(1,1), objectSize=(1,1)):
	row = int(img.width / (16*defaultSize[0]))
	x = (location % row) * 16 * defaultSize[0]
	y = (location // row) * 16 * defaultSize[1]
	return offset(img, -x, -y).crop((0,0, 16*objectSize[0], 16*objectSize[1]))

def loadTree(ss_tree, loc = 0):
	tree = Image.new('RGBA', (3*16, 6*16))
	body = cropImg(ss_tree, loc, objectSize=(3, 6))
	stump = cropImg(ss_tree, 20, objectSize=(1,2))
	tree.paste(stump, (1*16, 4*16), stump)
	tree.paste(body, (0,0) , body)
	return tree

def generateFarm(player, farm):

	season = player.getCurrentSeason()
	cache = {}
	craftable_blacklist = ['Twig', 'Torch', 'Sprinkler','Quality Sprinkler', 'Iridium Sprinkler']
	

	print('\tLoading Base...')
	farm_base = Image.open('./bases/{0}_base.png'.format(season))

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
					floor_type = cropImg(floor_sheet, item.type, (4, 4), (4, 4))
					cache['flooring-'+str(item.type)] = floor_type
			floor_view = cropImg(floor_type, item.orientation, objectSize=(1,1))
			farm_base.paste(floor_view, (item.x*16, item.y*16), floor_view)

		if item.name == 'HoeDirt':
			end  = ""
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
					floor_type = cropImg(floor_sheet, item.type, (4, 4), (4, 4))
					cache['flooring-'+str(item.type)] = floor_type
			floor_view = cropImg(floor_type, item.orientation, objectSize=(1,1))
			farm_base.paste(floor_view, (item.x*16, item.y*16), floor_view)

		if 'Crop' in item.name:
			crop_spritesheet = Image.open('./assets/farm/crops.png')
			crop_sprites = cropImg(crop_spritesheet, item.type,(7,2) ,(7,2))
			crop_img = cropImg(crop_sprites, item.growth, (1, 2), (1,2))
			if item.flipped: crop_img = crop_img.transpose(Image.FLIP_LEFT_RIGHT)
			farm_base.paste(crop_img, (item.x*16, item.y*16 - 16), crop_img)

		if item.name == 'Object':
			if item.type == "Crafting" and item.orientation not in craftable_blacklist:
				obj_img = cropImg(craftable_spritesheet, item.index, (1, 2), (1,2))
				offset = 16
			else:
				obj_img = cropImg(object_spritesheet, item.index)
				offset = 0
			farm_base.paste(obj_img, (item.x*16, item.y*16 - offset), obj_img)
		
		if item.name == 'Fence':
			fence_sheet = Image.open('./assets/farm/Fence{0}.png'.format(item.type))
			fence_img = cropImg(fence_sheet, item.orientation, defaultSize=(1,2), objectSize=(1,2))
			offset = 16
			farm_base.paste(fence_img, (item.x * 16, item.y * 16 - offset), fence_img)

		if item.name == 'ResourceClump':
			obj_img = cropImg(object_spritesheet, item.type, objectSize=(2,2))
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
						tree_crop = cropImg(tree_img, 18, objectSize=(1,2))
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
						tree_crop = cropImg(tree_img, item.growth + 1+ 9*item.type,defaultSize=(3,5), objectSize=(3, 5))
					else:
						tree_crop = cropImg(tree_img, 4 + seasons[season] + 9*item.type, defaultSize=(3,5), objectSize=(3, 5))
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

	return farm_base


def main():
	# f = 'Crono_116230451'
	for f in os.listdir(os.getcwd()+'/saves/'):
		print(f)
		p = player('./saves/'+f)
		generateFarm(p, getFarmInfo('./saves/'+f)).save('./farmRenders/' +f+'.png')

if __name__ == '__main__':
	main()