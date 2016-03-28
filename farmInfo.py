from defusedxml.ElementTree import parse
from defusedxml import ElementTree
from PIL import Image 
from collections import namedtuple

# This is a test method for returning the position location and the name of objects
# located on the players farm.
# 
# returns a dict with an array of tuples of the form: (name, x, y)
ns= "{http://www.w3.org/2001/XMLSchema-instance}"

def getFarmInfo(saveFileLocation,read_data=False):

	farm = {}

	if read_data == False:
		root = parse(saveFileLocation).getroot()
	else:
		root = ElementTree.fromstring(saveFileLocation)

	locations = root.find('locations').findall("GameLocation")

	farm['objects'] = []
	for item in locations[1].find('objects').iter("item"):
		name = item.find('value').find('Object').find('Name').text
		x = int(item.find('value').find('Object').find('tileLocation').find('X').text)
		y = int(item.find('value').find('Object').find('tileLocation').find('Y').text)
		l = int(item.find('value').find('Object').find('parentSheetIndex').text)
		t = item.find('value').find('Object').find('type').text
		if 'Fence' in name:
			t = int(item.find('value').find('Object').find('whichType').text)
		# if name not in things:
		# 	things.append(name)
		farm['objects'].append((name, x, y, l, t))

	farm['terrainFeatures'] = []
	for item in locations[1].find('terrainFeatures').iter('item'):
		s = None
		loc = None
		name = item.find('value').find('TerrainFeature').get(ns+'type')
		i = namedtuple('Item', ['name', 'x', 'y', 'sheetIndex','w', 'h', 'type', 'growth'])
		if name == 'Tree':
			t = int(item.find('value').find('TerrainFeature').find('treeType').text)
			s = int(item.find('value').find('TerrainFeature').find('growthStage').text)
		if name =='Flooring':
			t = int(item.find('value').find('TerrainFeature').find('whichFloor').text)
			s = int(item.find('value').find('TerrainFeature').find('whichView').text)
		x = int(item.find('key').find('Vector2').find('X').text)
		y = int(item.find('key').find('Vector2').find('Y').text)
		farm['terrainFeatures'] .append(i(name, x, y, loc, 1, 1, t, s))

	farm['resourceClumps'] = []
	for item in locations[1].find('resourceClumps').iter('ResourceClump'):
		t = int(item.find('parentSheetIndex').text)
		x = int(item.find('tile').find('X').text)
		y = int(item.find('tile').find('Y').text)
		w = int(item.find('width').text)
		h = int(item.find('height').text)
		farm['resourceClumps'].append((t,x, y, w, h))

	animal_habitable_buildings = ['Coop','Barn']

	farm['buildings'] = []
	farm['animals'] = []
	for item in locations[1].find('buildings').iter('Building'):
		name = item.find('buildingType').text 
		x = int(item.find('tileX').text)
		y = int(item.find('tileY').text)
		w = int(item.find('tilesWide').text)
		h = int(item.find('tilesHigh').text)
		t = item.find('buildingType').text
		farm['buildings'].append((name, x, y, w, h, t))
		
		if name in animal_habitable_buildings:
			for animal in item.find('indoors').find('animals').iter('item'):
				animal = animal.find('value').find('FarmAnimal')
				an = animal.find('name').text
				aa = int(animal.find('age').text)
				at = animal.find('type').text
				ah = int(animal.find('happiness').text)
				ahx = int(animal.find('homeLocation').find('X').text)
				ahy = int(animal.find('homeLocation').find('Y').text)
				farm['animals'].append((at,an,aa,ah,ahx,ahy))

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
	# generateImage(getFarmInfo('./saves/Crono_116230451')).save('farm.png')
	getFarmInfo('./saves/Crono_116230451')

if __name__ == '__main__':
	main()
