import os

from PIL import Image
from PIL.ImageOps import grayscale, colorize
from PIL.ImageChops import offset

from sdv import app


# Apply colour to image
def tintImage(img, tint):
    i = colorize(grayscale(img), (0, 0, 0), tint)
    i.putalpha(img.split()[3])
    return i


# Crops sprite from Spritesheet
def cropImg(img, location, defaultSize=(16, 16), objectSize=(16, 16), resize=False, displacement=(0, 0)):
    row = int(img.width / (defaultSize[0]))
    x = (location % row) * defaultSize[0]
    y = (location // row) * defaultSize[1]
    image = offset(img, -x, -y).crop((0, 0, objectSize[0], objectSize[1]))

    if resize:
        base = Image.new("RGBA", (16, 32), (0, 0, 0, 0))
        base.paste(image, displacement, image)
        image = base
    return image


# Paints a square a given colour
def colourBox(x, y, colour, pixels, scale=8):
    for i in range(scale):
        for j in range(scale):
            try:
                pixels[x*scale + i, y*scale + j] = colour
            except IndexError:
                pass
    return pixels


def watermark(img, mark=None):
    asset_dir = app.config.get('ASSET_PATH')
    if mark is None:
        mark = Image.open(os.path.join(asset_dir, 'logo.png'))
    x = 16
    y = img.size[1] - 16 - mark.size[1]
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    img.paste(mark, box=(x, y), mask=mark)
    return img.convert('P', palette=Image.ADAPTIVE, colors=255)
