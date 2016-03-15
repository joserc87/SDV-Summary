from defusedxml.ElementTree import parse
from defusedxml import ElementTree

def getStats(root):
    game_stats = {}
    stats_node = root.find('stats')
    for statistic in stats_node:
        stattag = statistic.tag[0].upper() + statistic.tag[1:]
        if stattag not in game_stats.keys():
            #check we're drawing info from the uppercase data and data not already exist
            if statistic.text != None:
                game_stats[stattag] = int(statistic.text)
            elif stattag == 'SpecificMonstersKilled':
                monsters = {}
                for monster in statistic.iter('item'):
                    monsterName = monster.find('key').find('string').text
                    count = int(monster.find('value').find('int').text)
                    monsters[monsterName] = count
                game_stats[stattag] = monsters
    return game_stats

def playerInfo(saveFileLocation,read_data=False):
    playerTags = ['name', 'isMale', 'farmName', 'favoriteThing', 'catPerson', 'deepestMineLevel', 'farmingLevel', 'miningLevel', 'combatLevel', 'foragingLevel', 'fishingLevel', 'professions', 'maxHealth', 'maxStamina', 'maxItems', 'money', 'totalMoneyEarned', 'millisecondsPlayed', 'friendships', 'shirt', 'hair', 'skin', 'accessory', 'facialHair', 'hairstyleColor', 'pantsColor', 'newEyeColor']
    professions = ['Rancher', 'Tiller', 'Coopmaster', 'Shepherd', 'Artisan', 'Agriculturist', 'Fisher', 'Trapper', 'Angler', 'Pirate', 'Mariner', 'Luremaster', 'Forester', 'Gatherer', 'Lumberjack', 'Tapper', 'Botanist', 'Tracker', 'Miner', 'Geologist', 'Blacksmith', 'Prospector', 'Excavator', 'Gemologist', 'Fighter', 'Scout', 'Brute', 'Defender', 'Acrobat', 'Desperado']

    ns= "{http://www.w3.org/2001/XMLSchema-instance}"
    if read_data == False:
        root = parse(saveFileLocation).getroot()
    else:
        root = ElementTree.fromstring(saveFileLocation)

    player = root.find("player")
    info = {}

    # Collect information stored in the player tag
    for tag in playerTags:
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
        if tag in ['name','farmName','favoriteThing']:
            if len(s)>34:
                raise IOError
        info[tag] = s

    # Information from elsewhere
    
    # UID for save file
    info['uniqueIDForThisGame'] = int(root.find('uniqueIDForThisGame').text)

    # Collecting player stats
    info['stats'] = getStats(root)

    # Collecting pet name
    petTypes = ['Cat', 'Dog']
    for location in root.find('locations').iter('GameLocation'):
        if location.get(ns+'type') == 'Farm' or location.get(ns+'type') == 'FarmHouse':
            for npc in location.find('characters').iter('NPC'):
                if npc.get(ns+'type') in petTypes:
                    info['petName'] = npc.find('name').text

    return info

def main():
    saveFile = "./save/Sketchy_116441313"
    saveFile = "./save/Jane_blahblah"
    print(playerInfo(saveFile))

if __name__ == '__main__':
    main()
