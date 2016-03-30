from PIL import Image
from PIL.ImageChops import offset
from playerInfo import player
from farmInfo import getFarmInfo

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

	print('\tRendering Flooring...')
	if 'Flooring' in farm:
		for tile, o in farm['Flooring']:
			if 'flooring-'+str(tile.type) in cache:
				floor_type = cache['flooring-'+str(tile.type)]
			else:
				with Image.open('./assets/farm/flooring.png') as floor_sheet:
					floor_type = cropImg(floor_sheet, tile.type, (4, 4), (4, 4))
					cache['flooring-'+str(tile.type)] = floor_type
			floor_view = cropImg(floor_type, o, objectSize=(1,1))
			farm_base.paste(floor_view, (tile.x*16, tile.y*16), floor_view)

	print('\tRendering Hoe Dirt...')
	if 'HoeDirt' in farm:
		for tile, o in farm['HoeDirt']:
			end  = ""
			if season == 'winter':
				end = "snow"
			hoe_sheet = Image.open('./assets/farm/hoeDirt' + end + '.png')
			hoe_tile = cropImg(hoe_sheet, o)
			farm_base.paste(hoe_tile, (tile.x*16, tile.y*16), hoe_tile)

	print('\tRendering Crops...')
	if 'Crops' in farm:
		for tile in sorted(farm['Crops'], key = lambda x: x[1]):
			crop_spritesheet = Image.open('./assets/farm/crops.png')
			crop_sprites = cropImg(crop_spritesheet, tile[3],(7,2) ,(7,2))
			crop_img = cropImg(crop_sprites, tile[2], (1, 2), (1,2))
			if tile[4]: crop_img = crop_img.transpose(Image.FLIP_LEFT_RIGHT)
			farm_base.paste(crop_img, (tile[0]*16, tile[1]*16 - 16), crop_img)

	print('\tRendering Terrain Features...')
	things = []
	for tFeat in farm['terrainFeatures']:
		if tFeat[0] not in things: things.append(tFeat[0])
	for thing in set(things):
		print('\t\t- '+thing)


	print('\tRendering Objects...')
	things = []
	other_things = []
	for obj in sorted(farm['objects'], key=lambda x: x[2]):
		if obj.type == "Crafting" and obj.name not in craftable_blacklist:
			if obj.name not in things: things.append(obj.name)
			obj_img = cropImg(craftable_spritesheet, obj.sheetIndex, (1, 2), (1,2))
			offset = 16
		else:
			if obj.name not in other_things: other_things.append(obj.name)
			obj_img = cropImg(object_spritesheet, obj.sheetIndex)
			offset = 0

		farm_base.paste(obj_img, (obj.x*16, obj.y*16 - offset), obj_img)
	
	print('\tRendering Fences...')
	if 'Fences' in farm:
		for fence, o in sorted(farm['Fences'], key = lambda x: x[0].y):
			fence_sheet = Image.open('./assets/farm/Fence{0}.png'.format(fence.type))
			fence_img = cropImg(fence_sheet, o, defaultSize=(1,2), objectSize=(1,2))
			offset = 16
			farm_base.paste(fence_img, (fence.x * 16, fence.y * 16 - offset), fence_img)

	print('\t2x1 Things')
	for thing in set(things):
		print('\t\t- '+thing)
	print('\t1x1 Things')
	for thing in set(other_things):
		print('\t\t- '+thing)


	print('\tRendering Resource Clumps...')
	for rClump in farm['resourceClumps']:
		obj_img = cropImg(object_spritesheet, rClump[0], objectSize=(2,2))
		farm_base.paste(obj_img, (rClump[1]*16, rClump[2]*16), obj_img)

	print('\tRendering Trees...')
	trees = [tree for tree in farm['terrainFeatures'] if tree[0] == 'Tree']
	for tree in sorted(trees, key = lambda x:x[2]):
		try:
			with Image.open('./assets/farm/tree{0}_{1}.png'.format(tree.type, season)) as tree_img:
				if tree.growth == 0:
					tree_crop = cropImg(tree_img, 26)
					offsetx = 0
					offsety = 0
				if tree.growth == 1:
					tree_crop = cropImg(tree_img, 24)
					offsetx = 0
					offsety = 0
				if tree.growth == 2:
					tree_crop = cropImg(tree_img, 25)
					offsetx = 0
					offsety = 0
				if tree.growth == 3 or tree.growth == 4:
					tree_crop = cropImg(tree_img, 18, objectSize=(1,2))
					offsetx = 0
					offsety = 16
				else:
					tree_crop = loadTree(tree_img)
					offsety = 5*16
					offsetx = 1*16
			if tree.flipped:
				tree_crop = tree_crop.transpose(Image.FLIP_LEFT_RIGHT)
			farm_base.paste(tree_crop, (tree[1]*16 - offsetx, tree[2]*16 - offsety), tree_crop)
		except Exception as e:
			print(e)

	print('\tRendering Fruit Trees...')
	fruitTrees = [ft for ft in farm['terrainFeatures'] if ft.name == 'FruitTree']
	for fruitTree in sorted(fruitTrees, key=lambda x:x.y):
		seasons = {'spring': 0, 'summer': 1, 'fall': 2, 'winter': 3}
		try:
			with Image.open('./assets/farm/fruitTrees.png') as tree_img:
				if fruitTree.growth <= 3:
					print(fruitTree.growth + 9*fruitTree.type)
					tree_crop = cropImg(tree_img, fruitTree.growth + 1+ 9*fruitTree.type,defaultSize=(3,5), objectSize=(3, 5))
				else:
					tree_crop = cropImg(tree_img, 4 + seasons[season] + 9*fruitTree.type, defaultSize=(3,5), objectSize=(3, 5))
				offsety = 4*16
				offsetx = 1*16
				if fruitTree.flipped:
					tree_crop = tree_crop.transpose(Image.FLIP_LEFT_RIGHT)
				farm_base.paste(tree_crop, (fruitTree.x*16 - offsetx, fruitTree.y*16 - offsety), tree_crop)
		except Exception as e:
			print(e)

	print('\tRendering Buildings...')
	for building in sorted(farm['buildings'], key=lambda x:x[2]):
		try:
			building_img = Image.open('./assets/farm/buildings/{0}.png'.format(building[5]))
			offsety = (building[4] - 1)*16
			farm_base.paste(building_img, (building[1]*16, building[2]*16 - offsety), building_img)
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