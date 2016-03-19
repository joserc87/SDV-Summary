import config
import sqlite3
import psycopg2
import json
from generateAvatar import generateAvatar
from generateFamilyPortrait import generateFamilyPortrait
from farmInfo import generateImage
import os
import time
from createdb import database_structure_dict, database_fields

IMAGE_FOLDER = 'static/images'

if config.USE_SQLITE == True:
	database = config.DB_SQLITE
	sqlesc = '?'
	def connect_db():
		return sqlite3.connect(database)
else:
	database = 'dbname='+config.DB_NAME+' user='+config.DB_USER+' password='+config.DB_PASSWORD
	sqlesc = '%s'
	def connect_db():
		return psycopg2.connect(database)

def process_queue():
	start_time = time.time()
	records_handled = 0
	db = connect_db()
	cur = db.cursor()
	while True:
		cur.execute('SELECT * FROM todo WHERE task='+sqlesc+'',('process_image',))
		tasks = cur.fetchall()
		# print tasks
		if len(tasks) != 0:
			for task in tasks:
				cur.execute('SELECT '+database_fields+' FROM playerinfo WHERE id=('+sqlesc+')',(task[2],))
				data = {}
				for i, item in enumerate(cur.fetchone()):
					data[sorted(database_structure_dict.keys())[i]] = item
				data['pantsColor'] = [data['pantsColor0'],data['pantsColor1'],data['pantsColor2'],data['pantsColor3']]
				data['newEyeColor'] = [data['newEyeColor0'],data['newEyeColor1'],data['newEyeColor2'],data['newEyeColor3']]
				data['hairstyleColor'] = [data['hairstyleColor0'],data['hairstyleColor1'],data['hairstyleColor2'],data['hairstyleColor3']]
				avatar = generateAvatar(data)
				if config.USE_SQLITE == True:
					pi = json.loads(data['portrait_info'])
				else:
					pi = data['portrait_info']
				portrait = generateFamilyPortrait(avatar, pi['partner'], pi['cat'], pi['children'])
				avatar_path = os.path.join(IMAGE_FOLDER,data['url']+'a.png')
				portrait_path = os.path.join(IMAGE_FOLDER,data['url']+'p.png')
				farm_path = os.path.join(IMAGE_FOLDER,data['url']+'f.png')
				avatar.save(avatar_path)
				portrait.save(portrait_path)
				farm = generateImage(json.loads(data['farm_info']))
				farm.save(farm_path)
				cur.execute('UPDATE playerinfo SET farm_url='+sqlesc+', avatar_url='+sqlesc+', portrait_url='+sqlesc+' WHERE id='+sqlesc+'',(farm_path,avatar_path,portrait_path,data['id']))
				cur.execute('DELETE FROM todo WHERE id=('+sqlesc+')',(task[0],))
				db.commit()
				records_handled += 1
		else:
			db.close()
			return time.time()-start_time, records_handled

if __name__ == "__main__":
	print(process_queue())
