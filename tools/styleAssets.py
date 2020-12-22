import os
from shutil import copy

dest_directory = os.getcwd() + os.path.join(os.path.sep, "sdv", "static")


def copy_images(file_names, src, dest):
    src_directory = os.getcwd() + os.path.join(os.path.sep, "assets", src)

    for file in file_names:
        try:
            src_file = os.path.join(src_directory, file[0])
            dest_file = os.path.join(dest_directory, dest)
            copy(src_file, dest_file)
            if file[1] is not None:
                os.rename(
                    os.path.join(dest_file, file[0]), os.path.join(dest_file, file[1])
                )
        except Exception as e:
            print(e)


def copyStyleAssets():
    css = [
        ("stardewPanorama.png", "bg.png"),
        ("textBox.png", None),
        ("DialogBoxGreen.png", "frame.png"),
    ]
    copy_images(css, os.path.join("loosesprites"), os.path.join("css"))


if __name__ == "__main__":
    copyStyleAssets()
