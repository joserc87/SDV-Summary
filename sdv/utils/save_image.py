import boto3
import io
import math
from flask import g
from flask import current_app as app

DO_REGION = app.config.get('DO_REGION')
DO_ENDPOINT = app.config.get('DO_ENDPOINT')
DO_ACCESS_KEY = app.config.get('DO_ACCESS_KEY')
DO_SECRET_KEY = app.config.get('DO_SECRET_KEY')

BUCKET = app.config.get('IMAGE_BUCKET')


def get_do_client():
    if 'client' not in g:
        session = boto3.session.Session()
        g.client = session.client('s3',
                                  region_name=DO_REGION,
                                  endpoint_url=DO_ENDPOINT,
                                  aws_access_key_id=DO_ACCESS_KEY,
                                  aws_secret_access_key=DO_SECRET_KEY,
                                  )
    return g.client


def upload_image(image, path):
    client = get_do_client()

    with io.BytesIO() as img_data:
        image.save(img_data, "PNG", compress_level=9)
        img_data.seek(0)
        client.put_object(ACL="public-read", Bucket=BUCKET, Key=path, Body=img_data)


def delete_images(farm_id, farm_url):
    client = get_do_client()

    base_subfolder = str(
        int(math.floor(int(farm_id) / app.config.get('IMAGE_MAX_PER_FOLDER')))
    )
    prefix = f"{base_subfolder}/{farm_url}"

    to_delete = client.list_objects(Bucket=BUCKET, Prefix=prefix)
    delete_keys = dict(Objects=[])
    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in to_delete.get('Contents', [])]]

    client.delete_objects(Bucket=BUCKET, Delete=delete_keys)
