import xml.etree.ElementTree

def playerInfo(saveFile):
    tags = [line.rstrip() for line in open("./data/player.txt", "r")]
    professions = [line.rstrip() for line in open("./data/professions.txt", "r")]

    root = xml.etree.ElementTree.parse(saveFile).getroot()

    player = root.find("player")
    info = {}

    for tag in tags:
        if player.find(tag).text != None:
            s = ""
            s = player.find(tag).text
        else:
            if tag == "profressions":
                s = []
                profs = player.find(tag)
                for a in profs.iter("int"):
                    s.append(professions[int(a.text)])
            if tag == "friendships":
                s = {}
                fship = player.find(tag)
                for item in fship:
                    name = item.find("key").find('string').text
                    rating = item.find('value').find('ArrayOfInt').find('int').text
                    s[name] = rating

        info[tag] = s
    return info

def main():
    saveFile = "./save/Sketchy_116441313"
    print(playerInfo(saveFile))

if __name__ == '__main__':
    main()
