import os
from shutil import copy
from PIL import Image

dest_directory = os.getcwd() + os.path.join(os.path.sep, 'sdv', 'assets')
src_directory = os.getcwd() + os.path.join(os.path.sep, 'assets')

def copy_images(file_names, src, dest):
    src_directory = os.getcwd() + os.path.join(os.path.sep, 'assets', src)
    for file in file_names:
        try:
            copy(os.path.join(src_directory, file), os.path.join(dest_directory, dest))
        except Exception as e:
            print(e)

def copy_player():
    misc = [
        'accessories.png',
        'hairstyles.png',
        'hats.png',
        'shirts.png',
        'shoeColors.png',
        'skinColors.png'
    ]

    copy_images(misc, os.path.join('Characters', 'Farmer'), os.path.join('player', 'misc'))

    genders = [
        'male',
        'female'
    ]

    for gender in genders:
        filename = 'farmer_base.png'
        if gender == 'female':
            filename = 'farmer_girl_base.png'
        assets = Image.open(os.path.join(src_directory, 'Characters', 'Farmer', filename))

        base = Image.new('RGBA', (16,32))
        arms = assets.crop((96, 0, 96 + 16, 32))
        arms.save(os.path.join(dest_directory, 'player', gender, '{}_arms.png'.format(gender)))
        base.paste(arms, mask=arms)
        body = assets.crop((0,0, 16, 24))
        base.paste(body, box=(0,0), mask=body)
        base.save(os.path.join(dest_directory, 'player', gender, '{}_base.png'.format(gender)))
        base.close()

        boots = Image.new('RGBA', (16,32))
        boot_asset = assets.crop((0,24, 16, 32))
        boots.paste(boot_asset, box=(0, 24), mask=boot_asset)
        boots.save(os.path.join(dest_directory, 'player', gender, '{}_boots.png'.format(gender)))
        boots.close()

        legs = Image.new('RGBA', (16, 32))
        leg_asset = assets.crop((288, 0, 288+16, 32))
        legs.paste(leg_asset, mask=leg_asset)
        legs.save(os.path.join(dest_directory, 'player', gender, '{}_legs.png'.format(gender)))
        legs.close()


if __name__ == '__main__':
    copy_player()