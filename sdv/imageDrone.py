import os
import time
import sqlite3
import psycopg2
import json
import math

from PIL import Image
from flask import Flask

import sdv.sql_commands as sql
from sdv.createdb import database_structure_dict, database_fields
from sdv.farmInfo import regenerateFarmInfo
from sdv.imagegeneration.avatar import generateAvatar
from sdv.imagegeneration.familyportrait import generateFamilyPortrait
from sdv.imagegeneration.farm import generateFarm, generateMinimap
from sdv.imagegeneration.tools import watermark
from sdv.parsers.json import parse_json
from sdv import app, connect_db, legacy_location
from sdv.utils.save_image import upload_image

sqlesc = app.sqlesc


def save_from_id(save_id, cursor):
    cursor.execute(
        'SELECT ' + database_fields + ' FROM playerinfo WHERE id=(' + sqlesc + ')',
        (save_id,)
    )
    result = cursor.fetchone()
    data = {key: value for key, value in zip(database_fields.split(','), result)}

    data['pantsColor'] = [data[f'pantsColor{i}'] for i in range(4)]
    data['newEyeColor'] = [data[f'newEyeColor{i}'] for i in range(4)]
    data['hairstyleColor'] = [data[f'hairstyleColor{i}'] for i in range(4)]

    return data


def process_queue():
    start_time = time.time()
    records_handled = 0
    db = connect_db()
    cur = db.cursor()

    while True:
        cur.execute(
            sql.GET_TODO_TASKS,
            (True, 'process_image',)
        )
        tasks = cur.fetchall()
        db.commit()

        if tasks:
            for task in tasks:
                task_id = task[0]
                farm_id = task[2]

                data = save_from_id(farm_id, cur)
                base_subfolder = str(
                    int(math.floor(int(farm_id) / app.config.get('IMAGE_MAX_PER_FOLDER')))
                )
                do_path = os.path.join('images', base_subfolder, data['url'])
                base_path = os.path.join(app.config.get('IMAGE_FOLDER'), base_subfolder, data['url'])

                try:
                    os.makedirs(legacy_location(base_path))
                except OSError:
                    pass

                base_path_fmt = os.path.join(base_path, data['url'] + '-{image_type}.png')
                do_path_fmt = os.path.join(do_path, data['url'] + '-{image_type}.png')

                # For compatibility reasons we're still saving the local paths
                avatar_path = base_path_fmt.format(image_type='a')
                portrait_path = base_path_fmt.format(image_type='p')
                farm_path = base_path_fmt.format(image_type='f')
                map_path = base_path_fmt.format(image_type='m')
                thumb_path = base_path_fmt.format(image_type='t')

                # New paths to store images in spaces
                do_avatar_path = do_path_fmt.format(image_type='a')
                do_portrait_path = do_path_fmt.format(image_type='p')
                do_farm_path = do_path_fmt.format(image_type='f')
                do_map_path = do_path_fmt.format(image_type='m')
                do_thumb_path = do_path_fmt.format(image_type='t')

                # Main Player Avatar and Portrait
                avatar = generateAvatar(data)
                avatar.resize((avatar.width * 4, avatar.height * 4))

                # Farmhands
                farmhands = data.get('farmhands', [])
                if farmhands:
                    for i, farmhand in enumerate(farmhands):
                        farmhand_path = base_path_fmt.format(
                            image_type=f'fh-{farmhand["UniqueMultiplayerID"]}'
                        )
                        do_farmhand_path = do_path_fmt.format(
                            image_type=f'fh-{farmhand["UniqueMultiplayerID"]}'
                        )
                        farmhand_avatar = generateAvatar(farmhand)

                        farmhand_avatar.resize((avatar.width * 4, avatar.height * 4))
                        upload_image(farmhand_avatar, do_farmhand_path)
                        farmhand_avatar.close()
                        farmhand['avatar_url'] = farmhand_path

                cur.execute(
                    sql.UPDATE_FARMHANDS,
                    (json.dumps(farmhands), farm_id)
                )

                portrait_info = json.loads(data['portrait_info'])

                partner_image = None
                partner_id = portrait_info.get('partner_id')
                if partner_id:
                    partner = next(filter(lambda f: f['UniqueMultiplayerID'] == partner_id, farmhands))
                    partner_image = Image.open(legacy_location(partner['avatar_url']))

                portrait = generateFamilyPortrait(avatar, portrait_info, partner_image=partner_image)

                # Minimap, Thumbnail and Main Map
                farm_data = regenerateFarmInfo(json.loads(data['farm_info']))
                minimap = generateMinimap(farm_data)

                farm = generateFarm(data['currentSeason'], farm_data)

                th = farm.resize((int(farm.width / 4), int(farm.height / 4)), Image.ANTIALIAS)
                farm = watermark(farm, filename='u.f.png')

                upload_image(portrait, do_portrait_path)
                upload_image(avatar, do_avatar_path)
                upload_image(th, do_thumb_path)
                upload_image(minimap, do_farm_path)
                upload_image(farm, do_map_path)

                farm.close()
                portrait.close()
                avatar.close()
                th.close()
                minimap.close()

                cur.execute(
                    sql.UPDATE_PLAYER_IMAGE_URLS,
                    (farm_path, avatar_path, portrait_path, map_path, thumb_path, base_path,
                     data['id'])
                )
                db.commit()

                cur.execute(sql.DELETE_TASK, (task_id,))
                db.commit()
                records_handled += 1
        else:
            db.close()
            return time.time() - start_time, records_handled


def process_plans():
    start_time = time.time()
    records_handled = 0
    db = connect_db()
    cur = db.cursor()
    while True:
        # cur.execute('SELECT * FROM todo WHERE task='+sqlesc+' AND currently_processing NOT TRUE',('process_image',))
        cur.execute(
            'UPDATE todo SET currently_processing=' + sqlesc + ' WHERE id=(SELECT id FROM todo WHERE task=' + sqlesc + ' AND currently_processing IS NOT TRUE LIMIT 1) RETURNING *',
            (True, 'process_plan_image',))
        tasks = cur.fetchall()
        db.commit()
        if len(tasks) != 0:
            for task in tasks:
                cur.execute('SELECT source_json, url, season FROM plans WHERE id=(' + sqlesc + ')',
                            (task[2],))
                result = cur.fetchone()
                farm_json = json.loads(result[0])
                url = result[1]
                season = 'spring' if result[2] == None else result[2]

                do_path = os.path.join('renders', url)
                base_path = os.path.join(app.config.get('RENDER_FOLDER'), url)
                try:
                    os.mkdir(legacy_location(base_path))
                except OSError:
                    pass
                try:
                    farm_data = parse_json(farm_json)

                    if farm_data['type'] == 'unsupported_map':
                        continue

                    farm_path = os.path.join(base_path, url + '-plan.png')
                    do_farm_path = os.path.join(do_path, url + '-plan.png')

                    farm = generateFarm(season, farm_data)
                    farm = watermark(farm, filename='stardew_info.png')
                    upload_image(farm, do_farm_path)

                    farm.close()

                    cur.execute(
                        'UPDATE plans SET image_url=' + sqlesc + ', base_path=' + sqlesc + ', render_deleted=FALSE, failed_render=NULL WHERE id=' + sqlesc + '',
                        (farm_path, base_path, task[2]))
                    db.commit()
                    # # except Exception as e:
                    # #     cur.execute('UPDATE playerinfo SET failed_processing='+sqlesc+' WHERE id='+,(True,data['id']))
                    # #     db.commit()
                    cur.execute('DELETE FROM todo WHERE id=(' + sqlesc + ')', (task[0],))
                    db.commit()
                except:
                    cur.execute('UPDATE plans SET failed_render=TRUE WHERE id=' + sqlesc,
                                (task[2],))
                    cur.execute('DELETE fROM todo WHERE id=(' + sqlesc + ')', (task[0],))
                records_handled += 1
        else:
            db.close()
            return time.time() - start_time, records_handled


if __name__ == "__main__":
    print(process_queue())
    # while True:
    # 	try:
    # print(process_queue())
    # 	time.sleep(5)
    # except KeyboardInterrupt:
    # 	exit()
