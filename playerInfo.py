import xml.etree.ElementTree

def playerInfo(saveFileLocation):
    tags = ['name', 'isMale', 'farmName', 'favoriteThing', 'catPerson', 'deepestMineLevel', 'farmingLevel', 'miningLevel', 'combatLevel', 'foragingLevel', 'fishingLevel', 'professions', 'maxHealth', 'maxStamina', 'maxItems', 'money', 'totalMoneyEarned', 'millisecondsPlayed', 'friendships', 'shirt', 'hair', 'skin', 'accessory', 'facialHair', 'hairstyleColor', 'pantsColor', 'newEyeColor']
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
                s = [professions[int(a.text)] for a in profs.iter("int")]
            if tag == "friendships":
                s = {}
                fship = player.find(tag)
                for item in fship:
                    name = item.find("key").find('string').text
                    rating = item.find('value').find('ArrayOfInt').find('int').text
                    s[name] = rating
            if tag in ['hairstyleColor', 'pantsColor', 'newEyeColor']:
                red = player.find(tag).find('R').text
                green = player.find(tag).find('G').text
                blue = player.find(tag).find('B').text
                alpha = player.find(tag).find('A').text
                s = [red, green, blue, alpha]

        info[tag] = s
    return info

def main():
    saveFile = "./save/Sketchy_116441313"
    print(playerInfo(saveFile))

if __name__ == '__main__':
    main()
