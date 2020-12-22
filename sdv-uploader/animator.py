import os
import glob
from urllib.parse import urljoin
import subprocess
import sys
from math import log

import requests

# import imageio
from PIL import Image, ImageFont, ImageDraw
from PyQt5 import QtCore

from ufapi import get_series_info
from config import root_directory, server_location, gifsicle_executable
from pyinstallerresourcesupport import resource_path

FONT_PATH = resource_path("fonts/VT323.ttf")
FINAL_PANEL_MULTIPLIER = 4


class AnimationThread(QtCore.QRunnable):
    def __init__(self, name, url, signal=None, **kwargs):
        super().__init__()
        self.name = name
        self.url = url
        self.signal = signal
        self.kwargs = kwargs
        self.button = kwargs.get("button")

    def run(self):
        filename = make_animation(self.name, self.url, **self.kwargs)
        if self.signal:
            self.signal.emit(filename, self.button)


def get_duration(n_frames):
    n = n_frames + FINAL_PANEL_MULTIPLIER - 1
    duration = log(n, 1.1) / (2.0 * n)
    return duration


def make_animation(name, url, **kwargs):
    """
    requests series info for URL, downloads missing files to root_directory+/animations/name,
    compiles animation
    """
    series_info = get_series_info(url)
    existing = prep_folder(name)
    data = get_new(series_info, existing, name)
    if kwargs.get("annotated") == True:
        files = [annotate_image(*i) for i in data]
    else:
        files = [open_image(i[0]) for i in data]
    duration = (
        get_duration(len(files))
        if kwargs.get("duration") == None or kwargs.get("duration") == 0
        else kwargs.get("duration")
    )
    # threshold = 0 if kwargs.get('threshold') == None else kwargs.get('threshold')
    if kwargs.get("type") == "gif":
        anim_type = "gif"
    else:
        anim_type = "gif"
    output_filename = os.path.join(
        animation_folder(name), "{}.{}".format(name, anim_type)
    )
    if anim_type == "gif":
        # imageio.plugins.freeimage.download()
        build_gif_with_pillow(files, output_filename, duration=duration)
    # elif anim_type == 'mp4':
    # 	imageio.plugins.ffmpeg.download()
    # 	build_mp4(files,output_filename,fps=1.0/duration)
    return output_filename


def animation_folder(name, sources=False):
    if sources == True:
        name = os.path.join(name, "sources")
    target = os.path.join(root_directory, "animations", name)
    return target


def prep_folder(name):
    target = animation_folder(name)
    os.makedirs(target, exist_ok=True)
    sources = animation_folder(name, sources=True)
    os.makedirs(sources, exist_ok=True)
    existing = []
    for item in glob.iglob(os.path.join(sources, "*.png")):
        existing.append(os.path.split(item)[1])
    return existing


def get_new(series_info, existing, name):
    data = []
    for entry in series_info.get("posts"):
        filename = os.path.split(entry[7])[1]
        file_path = os.path.join(animation_folder(name, sources=True), filename)
        if filename not in existing:
            server_path = entry[7].replace("\\", "/")
            url = urljoin(server_location, server_path)
            r = requests.get(url)
            if r.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(r.content)
        data.append([file_path] + entry[1:4])
    return data


# def build_gif_with_imageio(list_of_files,output_filename,**kwargs):
# 	duration = 1 if 'duration' not in kwargs else kwargs.get('duration')
# 	durations = [duration]*(len(list_of_files)-1) + [duration * FINAL_PANEL_MULTIPLIER]
# 	with imageio.get_writer(output_filename, mode='I', format='GIF-PIL', duration=durations, subrectangles=True) as writer:
# 		for file in list_of_files:
# 			image = imageio.imread(file)
# 			writer.append_data(image)


def build_gif_with_pillow(files, output_filename, **kwargs):
    duration = 1 if "duration" not in kwargs else kwargs.get("duration")
    durations = [duration * 1000] * (len(files) - 1) + [
        duration * 1000 * FINAL_PANEL_MULTIPLIER
    ]
    files[0].save(
        output_filename,
        save_all=True,
        append_images=files[1:],
        duration=durations,
        loop=0,
    )
    if gifsicle_executable:
        subprocess.run(
            [gifsicle_executable, "-b", "--colors", "256", "-O3", output_filename]
        )

        # if sys.platform == 'win32':
        # 	subprocess.run([gifsicle_executable,'-b','--colors','256','-O3',output_filename])
        # elif sys.platform == 'darwin':
        # 	try:
        # 		s = subprocess.Popen([gifsicle_executable,'-b',
        # 			'--colors','256','-O3',output_filename])
        # 		# ,env={'PATH':os.getenv('PATH')},
        # 		# shell=True, stdout = subprocess.PIPE,
        # 		# stderr=subprocess.STDOUT, stdin = subprocess.PIPE)
        # 		# with open(output_filename+'error.txt','wb') as f:
        # 		# 	f.write(str(s))
        # 	except OSError as e:
        # 		with open(output_filename+'error.txt','wb') as f:
        # 			f.write(str(e))


# def build_mp4_with_imageio(list_of_files,output_filename,**kwargs):
# 	fps = 1 if 'fps' not in kwargs else kwargs.get('fps')
# 	with imageio.get_writer(output_filename, mode='I',fps=fps) as writer:
# 		for file in list_of_files+[list_of_files[-1]]*(FINAL_PANEL_MULTIPLIER-1):
# 			image = imageio.imread(file)
# 			writer.append_data(image)


def annotate_image(filename, farmername, farmname, date):
    im = Image.open(filename).convert("RGBA")
    draw = ImageDraw.Draw(im)
    string1 = "{}, {} Farm".format(farmername, farmname)
    string2 = date
    font1 = ImageFont.truetype(FONT_PATH, 42)
    font2 = ImageFont.truetype(FONT_PATH, 42)
    w1, h1 = draw.textsize(string1, font=font1)
    w2, h2 = draw.textsize(string2, font=font2)
    # top right:
    # location1 = ((im.size[0]-w1)-5,0)
    # location2 = ((im.size[0]-w2)-5,h1)
    # across top:
    location1 = (5, 0)
    location2 = ((im.size[0] - w2) - 5, 0)
    _outline_text(draw, location1[0], location1[1], string1, font1)
    _outline_text(draw, location2[0], location2[1], string2, font2)
    draw.text(location1, string1, (255, 255, 255), font=font1)
    draw.text(location2, string2, (255, 255, 255), font=font2)
    # output_filename = '{}_a.png'.format(os.path.splitext(filename)[0])
    im = im.convert("P", palette=Image.ADAPTIVE, colors=256)
    # im.save(output_filename)
    # return output_filename
    return im


def open_image(filename):
    im = Image.open(filename).convert("RGBA")
    im = im.convert("P", palette=Image.ADAPTIVE, colors=256)
    return im


def _outline_text(draw, x, y, string, font):
    offset = 3
    locations = [
        (x + offset, y),
        (x - offset, y),
        (x, y + offset),
        (x, y - offset),
        (x - offset, y - offset),
        (x + offset, y - offset),
        (x - offset, y + offset),
        (x + offset, y + offset),
    ]
    for location in locations:
        draw.text(location, string, (0, 0, 0), font=font)


if __name__ == "__main__":
    result = make_animation("bigshaq_123456789", "1B3RNh", annotated=True, type="gif")
    # annotate_image(r'C:\Users\Femto\AppData\Roaming\upload.farm uploader\animations\bigshaq_123456789\1B3RO5-m.png','Big Shaq','MANS NOT HOT','1st of Spring, Year 5')
