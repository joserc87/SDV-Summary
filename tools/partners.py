from PIL import Image
import os

dest_directory = os.getcwd() + os.path.join(os.path.sep, 'sdv', 'assets')
src_directory = os.getcwd() + os.path.join(os.path.sep, 'assets')


def copy_partners():
    partners = [
        'Abigail.png',
        'Alex.png',
        'Elliott.png',
        'Haley.png',
        'Harvey.png',
        'Leah.png',
        'Maru.png',
        'Penny.png',
        'Sam.png',
        'Sebastian.png',
        'Shane.png',
        'Emily.png'
    ]
    for partner in partners:
        img = Image.open(os.path.join(src_directory, 'Characters', partner))
        img.crop((0, 0, 16, 32)).save(os.path.join(dest_directory, 'npcs', 'partners', partner))

if __name__ == '__main__':
    copy_partners()
