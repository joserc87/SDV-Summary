from defusedxml.ElementTree import parse
from defusedxml import ElementTree
from PIL import Image 
from collections import namedtuple

# Check adj. tiles for all tiles on map to determine orientation. Uses bit mask to  select correct tile from spritesheet
def checkSurrounding(tiles):
	floor_map = [[None for a in range(80)] for b in range(65)]
	for tile in tiles:
		floor_map[tile.y][tile.x] = tile

	temp = []
	m = []

	if tiles[0].name == 'Fence':
		m = [5, 3, 10, 6, 5, 3, 0, 6, 9, 8, 7, 7, 2, 8, 4, 4]
	else:
		m = [0, 12, 13, 9, 4, 8, 1, 5, 15, 11, 14, 10, 3, 7, 2, 6]

	for y, tile_row in enumerate(floor_map):
		for x, tile in enumerate(tile_row):
			a = 0
			if tile != None:
				for dx, dy, b in [(0,-1, 1),(1,0, 2),(0,1,4),(-1,0,8)]:
					try:
						if floor_map[y + dy][x + dx] != None:
							if tile.name == 'Flooring':
								if floor_map[y + dy][x + dx].type == tile.type:
									a += b
							else:
								a += b
					except Exception as e:
						print('Error: ' + str(e))
				temp.append((tile, m[a]))
	return temp


# This is a test method for returning the position location and the name of objects
# located on the players farm.
# 
# returns a dict with an array of tuples of the form: (name, x, y)

def getFarmInfo(saveFileLocation,read_data=False):
	i = namedtuple('Item', ['name', 'x', 'y', 'sheetIndex','w', 'h', 'type', 'growth', 'flipped'])

	ns= "{http://www.w3.org/2001/XMLSchema-instance}"

	farm = {}

	if read_data == False:
		root = parse(saveFileLocation).getroot()
	else:
		root = ElementTree.fromstring(saveFileLocation)

	locations = root.find('locations').findall("GameLocation")
	s = []
	for item in locations[1].find('objects').iter("item"):
		name = item.find('value').find('Object').find('Name').text
		x = int(item.find('value').find('Object').find('tileLocation').find('X').text)
		y = int(item.find('value').find('Object').find('tileLocation').find('Y').text)
		l = int(item.find('value').find('Object').find('parentSheetIndex').text)
		t = item.find('value').find('Object').find('type').text
		if 'Fence' in name:
			name = 'Fence'
			t = int(item.find('value').find('Object').find('whichType').text)
		# if name not in things:
		# 	things.append(name)
		s.append(i(name, x, y, l, 0, 0, t, None, None))

	d = {k[0]: [a for a in s if a[0] == k[0]] for k in s}

	try:
		farm['Fences'] = checkSurrounding(d['Fence'])
	except Exception as e:
		print('Error: ' + str(e))

	farm['objects'] = [a for a in s if a.name != 'Fence']

	tf = []
	crops = []

	for item in locations[1].find('terrainFeatures').iter('item'):
		s = None
		loc = None
		f = False
		name = item.find('value').find('TerrainFeature').get(ns+'type')
		if name == 'Tree':
			t = int(item.find('value').find('TerrainFeature').find('treeType').text)
			s = int(item.find('value').find('TerrainFeature').find('growthStage').text)
			if item.find('value').find('TerrainFeature').find('flipped').text == 'true': f= True
		if name =='Flooring':
			t = int(item.find('value').find('TerrainFeature').find('whichFloor').text)
			s = int(item.find('value').find('TerrainFeature').find('whichView').text)
		if name == "HoeDirt":
			if item.find('value').find('TerrainFeature').find('crop'):
				crop = item.find('value').find('TerrainFeature').find('crop')
				crop_x = int(item.find('key').find('Vector2').find('X').text)
				crop_y = int(item.find('key').find('Vector2').find('Y').text)
				crop_phase = int(crop.find('currentPhase').text)
				crop_location = int(crop.find('rowInSpriteSheet').text)
				crop_flip = False
				if crop.find('flip').text == 'true': crop_flip = True
				crop_dead = False
				if crop.find('dead').text == 'true': crop_dead = True
				crops.append((crop_x, crop_y, crop_phase, crop_location, crop_flip, crop_dead))
		x = int(item.find('key').find('Vector2').find('X').text)
		y = int(item.find('key').find('Vector2').find('Y').text)
		tf.append(i(name, x, y, loc, 1, 1, t, s, f))

	d = {k[0]: [a for a in tf if a[0] == k[0]] for k in tf}

	farm['terrainFeatures'] = tf
	farm['Crops'] = crops

	try:
		farm['Flooring'] = checkSurrounding(d['Flooring'])
		farm['HoeDirt'] = checkSurrounding(d['HoeDirt'])
	except Exception as e:
		print('Error: ' + str(e))

	s = []

	for item in locations[1].find('resourceClumps').iter('ResourceClump'):
		t = int(item.find('parentSheetIndex').text)
		x = int(item.find('tile').find('X').text)
		y = int(item.find('tile').find('Y').text)
		w = int(item.find('width').text)
		h = int(item.find('height').text)
		s.append((t,x, y, w, h))

	farm['resourceClumps'] = s

	s = []
	for item in locations[1].find('buildings').iter('Building'):
		name = item.find('buildingType').text 
		x = int(item.find('tileX').text)
		y = int(item.find('tileY').text)
		w = int(item.find('tilesWide').text)
		h = int(item.find('tilesHigh').text)
		t = item.find('buildingType').text
		s.append((name, x, y, w, h, t))

	farm['buildings'] = s

	return farm

def colourBox(x, y, colour, pixels, scale = 8):
	for i in range(scale):
		for j in range(scale):
			try:
				pixels[x*scale+ i, y*scale + j] = colour
			except IndexError:
				# print('IndexError making colorBox:',x,y,colour,pixels,scale)
				pass
	return pixels

# Renders a PNG of the players farm where one 8x8 pixel square is equivalent to one in game tile.
# Legend:	Shades of green - Trees, Weeds, Grass
# 		Shades of brown - Twigs, Logs
# 		Shades of grey - Stones, Boulders, Fences
# 		Dark red - Static buildings
# 		Light red - Player placed objects (Scarecrows, etc)
# 		Blue - Water
# 		Off Tan - Tilled Soil

def generateImage(farm):
	image = Image.open(".//data//img//base.png")
	pixels = image.load()

	pixels[1,1] = (255,255,255) 

	for building in farm['buildings']:
		for i in range(building[3]):
			for j in range(building[4]):
				colourBox(building[1] + i, building[2] + j, (255,150,150), pixels)

	for tile in farm['terrainFeatures']:
		name = tile[0]
		if name == "Tree":
			colourBox(tile[1], tile[2], (0,175,0), pixels)
		elif name == "Grass":
			colourBox(tile[1], tile[2], (0,125,0), pixels)
		elif name == "HoeDirt":
			colourBox(tile[1], tile[2], (196,196,38), pixels)
		elif name == "Flooring":
			colourBox(tile[1], tile[2], (50,50,50), pixels)
		else:
			colourBox(tile[1], tile[2], (0,0,0), pixels)

	for tile in farm['objects']:
		name= tile[0]
		if name == "Weeds":
			colourBox(tile[1], tile[2], (0,255,0), pixels)
		elif name == "Stone":
			colourBox(tile[1], tile[2], (125,125,125), pixels)
		elif name == "Twig":
			colourBox(tile[1], tile[2], (153,102,51), pixels)
		elif 'Fence' in name:
			colourBox(tile[1], tile[2], (200,200,200), pixels)
		else:
			colourBox(tile[1], tile[2], (255,0,0), pixels)

	for tile in farm['resourceClumps']:
		if tile[0] == 672:
			for i in range(tile[3]):
				for j in range(tile[3]):
					colourBox(tile[1] + i, tile[2] + j, (102, 51, 0), pixels)
		elif tile[0] == 600:
			for i in range(tile[3]):
				for j in range(tile[3]):
					colourBox(tile[1]+i, tile[2] + j, (75,75,75), pixels)

	return image

def main():
	getFarmInfo('./saves/Crono_116230451')

if __name__ == '__main__':
	main()
