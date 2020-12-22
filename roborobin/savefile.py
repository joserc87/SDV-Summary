from defusedxml.ElementTree import parse
from defusedxml import ElementTree


class savefile:
    """Hold onto the parse save game"""

    def __init__(self, saveFile, read_data=False):
        self.saveFile = saveFile
        if read_data == False:
            root = parse(saveFile).getroot()
        else:
            root = ElementTree.fromstring(saveFile)

        self.root = root

    def getRoot(self):
        return self.root


def get_location(root, name):
    locations = root.find("locations").findall("GameLocation")
    farm_location = None
    for location in locations:
        if (
            location.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type")
            == name
        ):
            farm_location = location
            break
    if farm_location == None:
        raise AttributeError
    return farm_location
