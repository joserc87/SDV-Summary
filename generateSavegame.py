from xml.etree.ElementTree import ElementTree, Element, SubElement, dump
from defusedxml import ElementTree as ET
import zipfile
import os

ns= "{http://www.w3.org/2001/XMLSchema-instance}"

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

def genSaveGameInfo(savegame_file):
	farmer = createFarmer(findPlayer(savegame_file))
	savegameinfo = ET.tostring(farmer, encoding='utf8', method='xml')
	return savegameinfo

def createZip(url,name,uniqueidforthisgame,static_folder,savegame_file):
	print 'this is triggering'
	target = os.path.join(static_folder,url+'.zip')
	folder = str(name)+'_'+str(uniqueidforthisgame)
	zf = zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED)
	zf.write(savegame_file,os.path.join(folder,folder),zipfile.ZIP_DEFLATED)
	zf.writestr(os.path.join(folder,'SaveGameInfo'),genSaveGameInfo(savegame_file))
	zf.writestr('upload.farm_instructions.txt','Downloaded from upload.farm!\n\nExtract the folder in this archive to %APPDATA%\\StardewValley\\Saves')
	zf.close()
	return target

if __name__=="__main__":
	static_folder = './static/saves/'
	savegame_file = './saves/iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii_117456659'
	import time
	start_time= time.time()
	print createZip('test','test','0123345678',static_folder,savegame_file)
	print time.time()-start_time