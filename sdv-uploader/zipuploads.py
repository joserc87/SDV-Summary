import zipfile
import os


def zopen(filename):
    """Designed to replace open() for zipped savegames."""
    try:
        file = _zopen(filename)
    except zipfile.BadZipfile:
        with open(filename, "r") as f:
            data = f.read()
        zwrite(data, filename)
        file = _zopen(filename)
    return file


def _zopen(filename):
    """Internal, no-fuss opening of zipfile."""
    # filename = os.path.splitext(filename)[0]
    zf = zipfile.ZipFile(filename, "r")
    file = zf.open(os.path.split(filename)[1], "r")
    zf.close()
    return file


def zwrite(data, filename, internal_filename=None):
    """Designed to replace saving unzipped save games."""
    if internal_filename == None:
        internal_filename = os.path.split(filename)[1]
    zf = zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_DEFLATED)
    if type(data) not in [str, bytes]:
        data = data.read()
    zf.writestr(internal_filename, data, zipfile.ZIP_DEFLATED)
    zf.close()
    return


def main():
    import app

    upload_folder = app.app.config["UPLOAD_FOLDER"]
    files = [
        "1AWerA",
        "1AWerH",
        "1AWeri",
        "1AWerO",
        "1AWerZ",
        "1AWes9",
        "1AXGWQ",
        "1AXHfd",
        "1AXIgW",
        "1AXIiB",
        "1B0WjE",
        "1B0Y4H",
    ]
    for file in files:
        zopen(os.path.join(upload_folder, file))


if __name__ == "__main__":
    main()
