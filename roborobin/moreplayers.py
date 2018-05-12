import io
import shutil
import time
import copy
import random

import xmltodict

from savefile import savefile
from farmInfo import getFarmInfo, generateImage

cabin_types = ["Plank Cabin", "Log Cabin", "Stone Cabin"]


def load_xml_to_memory(filename):
    with open(filename,'rb') as f:
    	memfile = io.BytesIO(f.read())
    return memfile


def write_memory_to_xml(memfile,filename):
	with open(filename,'w') as f:
		f.write(str(memfile.getvalue()))


def load_building():
	with open('buildings/building.xml','rb') as f:
		a = xmltodict.parse(f)
	return a


building_template = load_building()


def new_cabin(x,y,name_of_indoors,building_type):
	'''
	adds a cabin to the xml
	'''
	cabin = copy.deepcopy(building_template)
	cabin['Building']['tileX'] = x
	cabin['Building']['tileY'] = y
	cabin['Building']['nameOfIndoors'] = name_of_indoors
	assert building_type in cabin_types
	cabin['Building']['buildingType'] = building_type
	return cabin


class SaveGame:
	"""
	reads filename, creates:
		1. memfile, XML file stored in RAM
		2. xmldict, XML stored as a dict

	"""
	def __init__(self,filename,backup=True):
		if backup:
			shutil.copyfile(filename,filename+'_backup-{}'.format(str(time.time())))
		self.filename = filename
		self.load_filename()
		self._get_farm()
		self.v1_3()


	def v1_3(self):
		print(self.xmldict['SaveGame'].get('hasApplied1_3_UpdateChanges'))
		return False if self.xmldict['SaveGame'].get('hasApplied1_3_UpdateChanges') != 'true' else True


	def load_filename(self):
		with open(self.filename,'rb') as f:
			self.xmldict = xmltodict.parse(f.read())
			try:
				self.xmldict['SaveGame']
			except KeyError as e:
				raise e


	def add_cabin(self,cabin):
		self.farm['buildings']['Building'].append(cabin['Building'])


	def pop_cabin(self):
		self._last_cabin = None
		for b, building in enumerate(self.farm['buildings']['Building']):
			if building.get('indoors') and building.get('indoors').get('@xsi:type') == 'Cabin':
				self._last_cabin = b
		if self._last_cabin:
			self._last_cabin = self.farm['buildings']['Building'].pop(self._last_cabin)
		return self._last_cabin


	def _get_farm(self):
		for GameLocation in self.xmldict['SaveGame']['locations']['GameLocation']:
			if GameLocation.get('@xsi:type') == 'Farm':
				self.farm = GameLocation
				break


	def get_unique_cabin_name(self):
		self.get_cabins()
		self.cabin_names = []
		for cabin in self.cabins:
			try:
				self.cabin_names.append(cabin['nameOfIndoors'])
			except KeyError:
				pass
		while True:
			name = 'Cabin{}'.format(random.randint(0,1000000))
			if name not in self.cabin_names:
				break
		return name


	def get_cabins(self):
		self.cabins = []
		self._get_farm()
		for building in self.farm['buildings']['Building']:
			if building.get('indoors') and building.get('indoors').get('@xsi:type') == 'Cabin':
				self.cabins.append(building)
		# print(self.cabins)
		return self.cabins


	def save(self,filename):
		with open(filename,'w') as f:
			f.write(xmltodict.unparse(self.xmldict))


	def render(self,save=True,filename=None):
		for GameLocation in self.xmldict['SaveGame']['locations']['GameLocation']:
			if GameLocation.get('@xsi:type') == 'Farm':
				GameLocation = self.farm
		root = savefile(xmltodict.unparse(self.xmldict), True)
		data = getFarmInfo(root)
		image = generateImage(data)
		if save:
			if filename == None:
				filename = 'render.png'
			image.save(filename)
			return filename
		else:
			return image


if __name__ == "__main__":
	sg = SaveGame('OneDotThree_184790837',False)
	# cabin = new_cabin(60,62,'Cabin99999','Stone Cabin')
	# sg.add_cabin(cabin)
	# cabin2 = new_cabin(0,0,'Cabin97499','Plank Cabin')
	# sg.add_cabin(cabin2)
	# cabin3 = new_cabin(75,50,'Cabin97299','Log Cabin')
	# sg.add_cabin(cabin3)
	# sg.render()
	# sg.save()
	sg.get_unique_cabin_name()

	