import boto3
import io
import math
from flask import g
from flask import current_app as app


def get_bucket():
    return app.config.get('IMAGE_BUCKET')


def get_do_settings():
    DO_REGION = app.config.get('DO_REGION')
    DO_ENDPOINT = app.config.get('DO_ENDPOINT')
    DO_ACCESS_KEY = app.config.get('DO_ACCESS_KEY')
    DO_SECRET_KEY = app.config.get('DO_SECRET_KEY')

    return DO_REGION, DO_ENDPOINT, DO_ACCESS_KEY, DO_SECRET_KEY


def get_do_client():
    region, endpoint, access_key, secret_key = get_do_settings()

    if 'client' not in g:
        session = boto3.session.Session()
        g.client = session.client('s3',
                                  region_name=region,
                                  endpoint_url=endpoint,
                                  aws_access_key_id=access_key,
                                  aws_secret_access_key=secret_key,
                                  )
    return g.client


def upload_image(image, path):
    client = get_do_client()
    bucket = get_bucket()

    with io.BytesIO() as img_data:
        image.save(img_data, "PNG", compress_level=9)
        img_data.seek(0)
        client.put_object(ACL="public-read", Bucket=bucket, Key=path, Body=img_data)


def delete_directory(bucket, prefix):
    client = get_do_client()

    to_delete = client.list_objects(Bucket=bucket, Prefix=prefix)
    delete_keys = dict(Objects=[])
    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in to_delete.get('Contents', [])]]

    client.delete_objects(Bucket=bucket, Delete=delete_keys)


def delete_images(farm_id, farm_url):
    bucket = get_bucket()
    base_subfolder = str(
        int(math.floor(int(farm_id) / app.config.get('IMAGE_MAX_PER_FOLDER')))
    )
    prefix = f"images/{base_subfolder}/{farm_url}"

    delete_directory(bucket, prefix)


def delete_plan_render(plan_id):
    bucket = get_bucket()
    prefix = f"renders/{plan_id}"

    delete_directory(bucket, prefix)
