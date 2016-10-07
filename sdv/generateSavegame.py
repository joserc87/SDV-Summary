from xml.etree.ElementTree import ElementTree, Element, SubElement, dump
from defusedxml import ElementTree as ET
import zipfile
from sdv.zipuploads import zopen
import os
from sdv import legacy_location
import sys

if sys.version_info >= (3, 0):
	def str_or_bytes(string):
		return bytes(string,'utf-8')
else:
	def str_or_bytes(string):
		return string	

required_namespaces = '<Farmer xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
target_namespaces = '<Farmer xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'

def findPlayer(saveFileLocation,read_data=False):
	if read_data == False:
		root = ET.parse(saveFileLocation).getroot()
	else:
		root = ET.fromstring(saveFileLocation)
	player = root.find("player")
	return player

def createFarmer(player):
	farmer = Element('Farmer')
	for element in player.getchildren():
		if element.tag!='player':
			farmer.append(element)
	return farmer

def genSaveGameInfo(savegame_file,read_data=False):
	farmer = createFarmer(findPlayer(savegame_file,read_data))
	savegameinfo = ET.tostring(farmer, encoding='UTF-8', method='xml').strip(str_or_bytes('\r\n'))
	savegameinfo = savegameinfo.replace(str_or_bytes(target_namespaces),str_or_bytes(required_namespaces),1)
	return savegameinfo

def createZip(url,name,uniqueidforthisgame,static_folder,savegame_file):
	target = os.path.join(static_folder,url+'.zip')
	folder = str(name)+'_'+str(uniqueidforthisgame)
	zf = zipfile.ZipFile(legacy_location(target),'w',compression=zipfile.ZIP_DEFLATED)
	savegamedata = zopen(legacy_location(savegame_file)).read()
	zf.writestr(os.path.join(folder,folder),savegamedata,zipfile.ZIP_DEFLATED)
	zf.writestr(os.path.join(folder,'SaveGameInfo'),genSaveGameInfo(savegamedata,True))
	zf.writestr('upload.farm_instructions.txt','Downloaded from upload.farm/'+str(url)+'\r\n\r\nTo use, extract the folder in this archive to:\r\n%APPDATA%\\StardewValley\\Saves')
	zf.close()
	return target

if __name__=="__main__":
	static_folder = './static/saves/'
	savegame_file = './uploads/1AWerA'
	import time
	start_time= time.time()
	print(createZip('test','test','0123345678',static_folder,savegame_file))
	print(time.time()-start_time)