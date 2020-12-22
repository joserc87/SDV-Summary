from windows import launch
from setup import version
import os
import sys


__version__ = version


def main():
    try:
        directory = os.path.split(sys.argv[0])[0]
        os.chdir(directory)
    except:
        pass
    launch()


if __name__ == "__main__":
    main()
