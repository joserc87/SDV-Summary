import os
import time
import sqlite3
import psycopg2
import json

from PIL import Image
from flask import Flask

from sdv.createdb import database_structure_dict, database_fields
from sdv.farmInfo import regenerateFarmInfo
from sdv.imagegeneration.avatar import generateAvatar
from sdv.imagegeneration.familyportrait import generateFamilyPortrait
from sdv.imagegeneration.farm import generateFarm, generateMinimap
from sdv.parsers.json import parse_json
from sdv import app, connect_db, legacy_location
sqlesc = app.sqlesc


def process_queue():
    start_time = time.time()
    records_handled = 0
    db = connect_db()
    cur = db.cursor()
    while True:
        # cur.execute('SELECT * FROM todo WHERE task='+sqlesc+' AND currently_processing NOT TRUE',('process_image',))
        cur.execute('UPDATE todo SET currently_processing='+sqlesc+' WHERE id=(SELECT id FROM todo WHERE task='+sqlesc+' AND currently_processing IS NOT TRUE LIMIT 1) RETURNING *',(True,'process_image',))
        tasks = cur.fetchall()
        db.commit()
        if len(tasks) != 0:
            for task in tasks:
                cur.execute('SELECT '+database_fields+' FROM playerinfo WHERE id=('+sqlesc+')',(task[2],))
                result = cur.fetchone()
                data = {}
                for i, item in enumerate(result):
                    data[sorted(database_structure_dict.keys())[i]] = item
                data['pantsColor'] = [data['pantsColor0'],data['pantsColor1'],data['pantsColor2'],data['pantsColor3']]
                data['newEyeColor'] = [data['newEyeColor0'],data['newEyeColor1'],data['newEyeColor2'],data['newEyeColor3']]
                data['hairstyleColor'] = [data['hairstyleColor0'],data['hairstyleColor1'],data['hairstyleColor2'],data['hairstyleColor3']]

                base_path = os.path.join(app.config.get('IMAGE_FOLDER'), data['url'])
                try:
                    os.mkdir(legacy_location(base_path))
                except OSError:
                    pass

                avatar_path = os.path.join(base_path, data['url']+'-a.png')
                avatar = generateAvatar(data)

                pi = json.loads(data['portrait_info'])
                portrait_path = os.path.join(base_path, data['url']+'-p.png')
                generateFamilyPortrait(avatar, pi).save(legacy_location(portrait_path), compress_level=9)

                avatar.resize((avatar.width*4, avatar.height*4)).save(legacy_location(avatar_path), compress_level=9)

                farm_data = regenerateFarmInfo(json.loads(data['farm_info']))
                farm_path = os.path.join(base_path, data['url']+'-f.png')
                generateMinimap(farm_data).save(legacy_location(farm_path), compress_level=9)

                map_path = os.path.join(base_path, data['url']+'-m.png')
                thumb_path = os.path.join(base_path, data['url']+'-t.png')
                farm = generateFarm(data['currentSeason'], farm_data)
                th = farm.resize((int(farm.width/4), int(farm.height/4)), Image.ANTIALIAS)
                th.save(legacy_location(thumb_path))
                farm.save(legacy_location(map_path), compress_level=9)

                cur.execute('UPDATE playerinfo SET farm_url='+sqlesc+', avatar_url='+sqlesc+', portrait_url='+sqlesc+', map_url='+sqlesc+', thumb_url='+sqlesc+', base_path='+sqlesc+' WHERE id='+sqlesc+'',(farm_path,avatar_path,portrait_path,map_path,thumb_path,base_path,data['id']))
                db.commit()
                # except Exception as e:
                #     cur.execute('UPDATE playerinfo SET failed_processing='+sqlesc+' WHERE id='+,(True,data['id']))
                #     db.commit()
                cur.execute('DELETE FROM todo WHERE id=('+sqlesc+')',(task[0],))
                db.commit()
                records_handled += 1
        else:
            db.close()
            return time.time()-start_time, records_handled

def process_plans():
    start_time = time.time()
    records_handled = 0
    db = connect_db()
    cur = db.cursor()
    while True:
        # cur.execute('SELECT * FROM todo WHERE task='+sqlesc+' AND currently_processing NOT TRUE',('process_image',))
        cur.execute('UPDATE todo SET currently_processing='+sqlesc+' WHERE id=(SELECT id FROM todo WHERE task='+sqlesc+' AND currently_processing IS NOT TRUE LIMIT 1) RETURNING *',(True,'process_plan_image',))
        tasks = cur.fetchall()
        db.commit()
        if len(tasks) != 0:
            for task in tasks:
                cur.execute('SELECT source_json, url, season FROM plans WHERE id=('+sqlesc+')',(task[2],))
                result = cur.fetchone()
                farm_json = json.loads(result[0])
                url = result[1]
                season = 'spring' if result[2] == None else result[2]

                base_path = os.path.join(app.config.get('RENDER_FOLDER'), url)
                try:
                    os.mkdir(legacy_location(base_path))
                except OSError:
                    continue

                farm_data = parse_json(farm_json)
                
                if farm_data['type'] == 'unsupported_map':
                    continue

                farm_path = os.path.join(base_path, url+'-plan.png')
                # generateMinimap(farm_data).save(legacy_location(farm_path), compress_level=9)

                # map_path = os.path.join(base_path, data['url']+'-m.png')
                # thumb_path = os.path.join(base_path, data['url']+'-t.png')
                farm = generateFarm(season, farm_data)
                # th = farm.resize((int(farm.width/4), int(farm.height/4)), Image.ANTIALIAS)
                # th.save(legacy_location(thumb_path))
                farm.save(legacy_location(farm_path), compress_level=9)

                cur.execute('UPDATE plans SET image_url='+sqlesc+', base_path='+sqlesc+' WHERE id='+sqlesc+'',(farm_path,base_path,task[2]))
                db.commit()
                # # except Exception as e:
                # #     cur.execute('UPDATE playerinfo SET failed_processing='+sqlesc+' WHERE id='+,(True,data['id']))
                # #     db.commit()
                cur.execute('DELETE FROM todo WHERE id=('+sqlesc+')',(task[0],))
                db.commit()
                records_handled += 1
        else:
            db.close()
            return time.time()-start_time, records_handled

if __name__ == "__main__":
    print(process_queue())
    # while True:
    # 	try:
            # print(process_queue())
        # 	time.sleep(5)
        # except KeyboardInterrupt:
        # 	exit()
