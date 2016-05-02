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
