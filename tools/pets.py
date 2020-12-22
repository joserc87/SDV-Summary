import os
from PIL import Image

dest_directory = os.getcwd() + os.path.join(os.path.sep, "sdv", "assets")
src_directory = os.getcwd() + os.path.join(os.path.sep, "assets")


def copy_pets():
    animals = ["Dog.png", "Cat.png"]

    for animal in animals:
        img = Image.open(os.path.join(src_directory, "Animals", animal))
        img.crop((64, 130, 64 + 32, 130 + 32)).save(
            os.path.join(dest_directory, "npcs", "animals", animal)
        )


if __name__ == "__main__":
    copy_pets()
