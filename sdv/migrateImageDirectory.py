import psycopg2
import shutil
import os
import math
from sdv.createdb import database_structure_dict, database_fields
from sdv import app, connect_db, legacy_location
sqlesc = app.sqlesc

def processFile(rowid, original_base_path, original_avatar_path, original_portrait_path, original_farm_path, original_map_path, original_thumb_path, url):
	if url == None:
		return None

	base_subfolder = str(int(math.floor(int(rowid)/app.config.get('IMAGE_MAX_PER_FOLDER'))))
	base_path = os.path.join(app.config.get('IMAGE_FOLDER'), base_subfolder, url)

	if base_path == original_base_path:
		return None

	try:
		os.makedirs(legacy_location(base_path))
	except OSError:
		pass

	try:
		connection = connect_db()
		cur = connection.cursor()

		avatar_paths = [original_avatar_path, os.path.join(base_path, url+'-a.png')]
		portrait_paths = [original_portrait_path, os.path.join(base_path, url+'-p.png')]
		farm_paths = [original_farm_path, os.path.join(base_path, url+'-f.png')]
		map_paths = [original_map_path, os.path.join(base_path, url+'-m.png')]
		thumb_paths = [original_thumb_path, os.path.join(base_path, url+'-t.png')]

		for original, new in [avatar_paths,portrait_paths,farm_paths,map_paths,thumb_paths]:
			try:
				shutil.move(legacy_location(original),legacy_location(new))
			except IOError:
				pass
		try:
			os.rmdir(legacy_location(original_base_path))
		except WindowsError:
			pass

		cur.execute('UPDATE playerinfo SET base_path = '+sqlesc+', avatar_url = '+sqlesc+', portrait_url = '+sqlesc+', farm_url = '+sqlesc+', map_url = '+sqlesc+', thumb_url = '+sqlesc+' WHERE id='+sqlesc,(base_path,avatar_paths[1],portrait_paths[1],farm_paths[1],map_paths[1],thumb_paths[1],rowid))
		connection.commit()
		return True
	except:
		return False


def getEntries(where=None):
	connection = connect_db()
	c = connection.cursor()
	if where==None:
		where=''
	c.execute('SELECT id, base_path, avatar_url, portrait_url, farm_url, map_url, thumb_url, url FROM playerinfo '+where)
	entries = c.fetchall()
	connection.close()
	return entries

def main():
	entries = getEntries()
	failures = []
	for eno, entry in enumerate(entries):
		result = processFile(*entry)
		if result != True:
			print(entry[0:2],' had result ',result)
			failures.append([entry[0],entry[1],result])
		print(eno+1,'of',len(entries))

	print('failures')
	print(failures)


if __name__ == "__main__":
	main()
