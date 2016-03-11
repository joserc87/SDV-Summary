import config
import sqlite3
import json
from generateAvatar import generateAvatar
from farmInfo import generateImage
import os
import time

IMAGE_FOLDER = 'static/images'
database = config.db

def connect_db():
	return sqlite3.connect(database)

def process_queue():
	start_time = time.time()
	records_handled = 0
	db = connect_db()
	cur = db.cursor()
	while True:
		cur.execute('SELECT * FROM todo WHERE task="process_image"')
		tasks = cur.fetchall()
		#print tasks
		if len(tasks) != 0:
			for task in tasks:
				cur.execute('SELECT id, url, pantsColor0, pantsColor1,pantsColor2, pantsColor3, hairstyleColor0, hairstyleColor1, hairstyleColor2, hairstyleColor3, hair, shirt, farm_info FROM playerinfo WHERE id=(?)',(task[2],))
				data = cur.fetchone()
				rowid, url = data[0:2]
				player_info = {}
				player_info['pantsColor'] = data[2:6]
				player_info['hairstyleColor'] = data[6:10]
				player_info['hair'] = data[10]
				player_info['shirt'] = data[11]
				farm_info = json.loads(data[12])
				avatar = generateAvatar(player_info)
				avatar_path = os.path.join(IMAGE_FOLDER,url+'a.png')
				farm_path = os.path.join(IMAGE_FOLDER,url+'f.png')
				avatar.save(avatar_path)
				farm = generateImage(farm_info)
				farm.save(farm_path)
				cur.execute('UPDATE playerinfo SET farm_url=?, avatar_url=? WHERE id=?',(farm_path,avatar_path,rowid))
				db.execute('DELETE FROM todo WHERE id=(?)',(task[0],))
				db.commit()
				records_handled += 1
		else:
			db.close()
			return time.time()-start_time, records_handled

if __name__ == "__main__":
	print process_queue()
