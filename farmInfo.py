import xml.etree.ElementTree

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
		x = item.find('value').find('Object').find('tileLocation').find('X').text
		y = item.find('value').find('Object').find('tileLocation').find('Y').text
		s.append((name, x, y))

	farm['objects'] = s

	return farm

def main():
	print(getFarmInfo('./save/Sketchy_116441313'))

if __name__ == '__main__':
	main()
