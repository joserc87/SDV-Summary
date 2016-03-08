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
	s = []
	for item in locations[1].find('objects').iter("item"):
		name = item.find('value').find('Object').find('Name').text
		x = int(item.find('value').find('Object').find('tileLocation').find('X').text)
		y = int(item.find('value').find('Object').find('tileLocation').find('Y').text)
		s.append((name, x, y))

	farm['objects'] = s

	return s

def colourBox(x, y, colour, pixels, scale = 8):
	for i in range(scale):
		for j in range(scale):
			pixels[x*scale+ i, y*scale + j] = colour
	return pixels

def makeImage():
	newImage = Image.new('RGB', (80*8, 70*8))
	pixels = newImage.load()
	for i in range(80*8):
		for j in range(70*8):
			pixels[i,j] = (255, 224, 102)

	farm = getFarmInfo('./save/Sketchy_116441313')

	for tile in farm:
		if tile[0] == "Weeds":
			colourBox(tile[1], tile[2], (0,255,0), pixels)
		elif tile[0] == "Stone":
			colourBox(tile[1], tile[2], (125,125,125), pixels)
		elif tile[0] == "Twig":
			colourBox(tile[1], tile[2], (153,102,51), pixels)
		elif tile[0] != "Chest":
			colourBox(tile[1], tile[2], (255,0,0), pixels)

	newImage.save("test.png")

def main():
	getFarmInfo('./save/Sketchy_116441313')
	makeImage()

if __name__ == '__main__':
	main()
