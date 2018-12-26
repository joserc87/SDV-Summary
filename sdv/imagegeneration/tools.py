import os

from PIL import Image, ImageFont, ImageDraw
from PIL.ImageOps import grayscale, colorize
from PIL.ImageChops import offset

from sdv.app import app


# Apply colour to image
def tintImage(img, tint):
    i = colorize(grayscale(img), (0, 0, 0), tint)
    i.putalpha(img.split()[3])
    return i


# Crops sprite from Spritesheet
def cropImg(img, location, defaultSize=(16, 16), objectSize=(16, 16), resize=False,
            displacement=(0, 0)):
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
                pixels[x * scale + i, y * scale + j] = colour
            except IndexError:
                pass
    return pixels


def watermark(img, mark=None, filename='u.f.png', text=None):
    asset_dir = app.config.get('ASSET_PATH')

    if mark is None:
        mark = Image.open(os.path.join(asset_dir, 'watermarks', filename))

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    if text is not None:
        font = ImageFont.truetype(
                os.path.join(app.config.get('BASE_DIR'), 'sdv', 'static', 'fonts', 'VT323-Regular.ttf'),
                16
        )
        draw = ImageDraw.Draw(img)

        padding = {'x': 10, 'y': 2}
        w, h = font.getsize(text)

        text_x = img.size[0] - 16 - w
        text_y = img.size[1] - 16 - h

        draw.rectangle(
                (text_x - padding['x'], text_y, text_x + w + padding['x'], text_y + h + padding['y']),
                fill='black'
        )
        draw.text((text_x, text_y), text, 'white', font=font)
        del draw

    x = 16
    y = img.size[1] - 16 - mark.size[1]

    img.paste(mark, box=(x, y), mask=mark)
    img.convert('P', palette=Image.ADAPTIVE, colors=255)

    return img
