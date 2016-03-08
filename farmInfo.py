import xml.etree.ElementTree
from PIL import Image 

# This is a test method for returning the position location and the name of objects
# located on the players farm.
# 
# returns a dict with an array of tuples of the form: (name, x, y)

def getFarmInfo(saveFileLocation):
	ns= "{http://www.w3.org/2001/XMLSchema-instance}"

	farm = {}

	root = xml.etree.ElementTree.parse(saveFileLocation).getroot()

	locations = root.find('locations').findall("GameLocation")
	# things = []
	s = []
	for item in locations[1].find('objects').iter("item"):
		name = item.find('value').find('Object').find('Name').text
		x = int(item.find('value').find('Object').find('tileLocation').find('X').text)
		y = int(item.find('value').find('Object').find('tileLocation').find('Y').text)
		# if name not in things:
		# 	things.append(name)
		s.append((name, x, y))

	# print(things)

	farm['objects'] = s

	s = []

	for item in locations[1].find('terrainFeatures').iter('item'):
		name = item.find('value').find('TerrainFeature').get(ns+'type')
		x = int(item.find('key').find('Vector2').find('X').text)
		y = int(item.find('key').find('Vector2').find('Y').text)
		s.append((name, x, y))

	farm['terrainFeatures'] = s

	s = []

	for item in locations[1].find('resourceClumps').iter('ResourceClump'):
		x = int(item.find('tile').find('X').text)
		y = int(item.find('tile').find('Y').text)
		w = int(item.find('width').text)
		h = int(item.find('height').text)
		s.append((x, y, w, h))

	farm['resourceClumps'] = s

	return farm

def colourBox(x, y, colour, pixels, scale = 8):
	for i in range(scale):
		for j in range(scale):
			pixels[x*scale+ i, y*scale + j] = colour
	return pixels

def generateImage():
	image = Image.open(".//data//img//base.png")
	pixels = image.load()

	farm = getFarmInfo('./save/Sketchy_116441313')

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
		elif name != "Chest":
			colourBox(tile[1], tile[2], (255,0,0), pixels)

	for tile in farm['resourceClumps']:
		for i in range(tile[2]):
			for j in range(tile[3]):
				colourBox(tile[0] + i, tile[1] + j, (75,75,75), pixels)


	image.save("test.png")

def main():
	getFarmInfo('./save/Sketchy_116441313')
	generateImage()

if __name__ == '__main__':
	main()
