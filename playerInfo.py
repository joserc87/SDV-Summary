import xml.etree.ElementTree

def playerInfo(saveFileLocation):
    tags = ['name', 'isMale', 'farmName', 'favoriteThing', 'catPerson', 'deepestMineLevel', 'farmingLevel', 'miningLevel', 'combatLevel', 'foragingLevel', 'fishingLevel', 'professions', 'maxHealth', 'maxStamina', 'maxItems', 'money', 'totalMoneyEarned', 'millisecondsPlayed', 'friendships']
    professions = ['Rancher', 'Tiller', 'Coopmaster', 'Shepherd', 'Artisan', 'Agriculturist', 'Fisher', 'Trapper', 'Angler', 'Pirate', 'Mariner', 'Luremaster', 'Forester', 'Gatherer', 'Lumberjack', 'Tapper', 'Botanist', 'Tracker', 'Miner', 'Geologist', 'Blacksmith', 'Prospector', 'Excavator', 'Gemologist', 'Fighter', 'Scout', 'Brute', 'Defender', 'Acrobat', 'Desperado']

    root = xml.etree.ElementTree.parse(saveFileLocation).getroot()

    player = root.find("player")
    info = {}

    for tag in tags:
        if player.find(tag).text != None:
            s = player.find(tag).text
        else:
            if tag == "professions":
                profs = player.find(tag)
                s = [int(a.text) for a in profs.iter("int")]
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
