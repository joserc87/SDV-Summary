from threading import Thread

from setup import version
from distutils.version import LooseVersion
from ufapi import get_uploader_version


def version_is_current():
    input_list = []
    t = Thread(target=_get_version, args=(input_list,))
    t.start()
    t.join(2)
    if len(input_list) == 0:
        return True
    else:
        return input_list[0]


def _get_version(input_list):
    try:
        remote = get_uploader_version()["version"]
        local = version
        input_list.append(LooseVersion(local) >= LooseVersion(remote))
        return
    except:
        input_list.append(True)
        return


def main():
    print(version_is_current())


if __name__ == "__main__":
    main()
