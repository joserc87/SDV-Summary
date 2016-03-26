from defusedxml.ElementTree import parse
from defusedxml import ElementTree
from PIL import Image 
from collections import namedtuple
import glob

folder = './uploads/*'

files = glob.glob(folder)

structure = {}

def moveRecursivelyOverXml(element):
	reconstructed_dict = {}
	if element.getchildren() == []:
		reconstructed_dict = element.text
	else:
		for child in element.getchildren():
			if element.attrib != {}:
				reconstructed_dict.update(element.attrib)
			reconstructed_dict[child.tag] = moveRecursivelyOverXml(child)
	return reconstructed_dict

def main():
	for f, file in enumerate(files[0:1]):
		ns = "{http://www.w3.org/2001/XMLSchema-instance}"
		locations = parse(file).getroot().find('locations').findall('GameLocation')
		assert locations[1].attrib[ns+'type'] == 'Farm'
		farm = locations[1]
		print(str(f)+' of '+str(len(files)-1))
		structure.update(moveRecursivelyOverXml(farm))
	# print structure
	return structure

if __name__ == "__main__":
	structure = main()
	print structure
	
