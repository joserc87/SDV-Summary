from defusedxml.ElementTree import parse
from defusedxml import ElementTree
import json

ns = "{http://www.w3.org/2001/XMLSchema-instance}"
animal_habitable_buildings = ['Coop', 'Barn', 'SlimeHutch']


class player:
    """docstring for player"""
    def __init__(self, saveFile):
        # super(player, self).__init__()
        self.saveFile = saveFile
        self.eTree = parse(saveFile)
        self.root = self.eTree.getroot()

    def getPlayerInfo(self):
        return playerInfo(self.saveFile)

    def getAchievements(self):
        achievements = [int(achievement.text) for achievement in self.root.find('player').find('achievements').iter('int')]
        print(achievements)


def getPartners(root):
    partners = []
    for location in root.find('locations').iter('GameLocation'):
        for npc in location.iter('NPC'):
            if int(npc.find('daysMarried').text) > 0:
                partners.append(npc)
    return partners


def getChildren(root):
    children = []
    childType = ['Child']
    childLocation = ['Farm', 'FarmHouse']
    child_nodes = getNPCs(root, childLocation, childType)
    return child_nodes


def getStats(root):
    game_stats = {}
    stats_node = root.find('stats')
    for statistic in stats_node:
        stattag = statistic.tag[0].upper() + statistic.tag[1:]
        if stattag not in game_stats.keys():
            # check we're drawing info from the uppercase data and data not already exist
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


def getNPCs(root, loc, types):
    npc_list = []
    for location in root.find('locations').iter('GameLocation'):
        if location.get(ns+'type') in loc:
            NPCs = location.find('characters').iter('NPC')
            npc_list += [npc for npc in NPCs if npc.get(ns+'type') in types]
    return npc_list


def getAnimals(root):
    locations = root.find('locations').findall("GameLocation")
    animals = {}
    for item in locations[1].find('buildings').iter('Building'):
        buildingtype = item.get(ns+'type')
        name = item.find('buildingType').text 
        if buildingtype in animal_habitable_buildings:
            for animal in item.find('indoors').find('animals').iter('item'):
                animal = animal.find('value').find('FarmAnimal')
                an = animal.find('name').text
                aa = int(animal.find('age').text)
                at = animal.find('type').text
                ah = int(animal.find('happiness').text)
                ahx = int(animal.find('homeLocation').find('X').text)
                ahy = int(animal.find('homeLocation').find('Y').text)
                animaltuple = (an,aa,ah,ahx,ahy,name)
                try:
                    animals[at].append(animaltuple)
                except KeyError:
                    animals[at] = [animaltuple]
    horse = getNPCs(root,['Farm'],['Horse'])
    if horse != []:
        animals['horse']=horse[0].find('name').text
    return animals


def strToBool(x):
    if x.lower() == 'true':
        return True
    else:
        return False


def playerInfo(saveFileLocation,read_data=False):
    playerTags = ['name', 'isMale', 'farmName', 'favoriteThing', 'catPerson', 'deepestMineLevel', 'farmingLevel',
                'miningLevel', 'combatLevel', 'foragingLevel', 'fishingLevel', 'professions', 'maxHealth', 'maxStamina',
                'maxItems', 'money', 'totalMoneyEarned', 'millisecondsPlayed', 'friendships', 'shirt', 'hair', 'skin',
                'accessory', 'facialHair', 'hairstyleColor', 'pantsColor', 'newEyeColor','dateStringForSaveGame']
    professions = ['Rancher', 'Tiller', 'Coopmaster', 'Shepherd', 'Artisan', 'Agriculturist', 'Fisher', 'Trapper',
                'Angler', 'Pirate', 'Mariner', 'Luremaster', 'Forester', 'Gatherer', 'Lumberjack', 'Tapper', 'Botanist',
                'Tracker','Miner', 'Geologist', 'Blacksmith', 'Prospector', 'Excavator', 'Gemologist', 'Fighter', 'Scout',
                'Brute', 'Defender','Acrobat', 'Desperado']
    npcs = ['Willy','Clint','Jodi','Harvey','Leah','Wizard','Jas','Abigail','Maru','Elliott','Caroline','Pam','Dwarf',
            'Shane','Demetrius','Alex','Gus','Vincent','Sebastian','Robin','Sam','Lewis','Marnie','Penny','Haley','Pierre',
            'Evelyn','Linus','George','Emily','Kent','Krobus','Sandy']
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
                    if name in npcs:
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
        if tag == 'dateStringForSaveGame':
            tag = 'date'
        info[tag] = s


    # Information from elsewhere    
    # UID for save file
    info['uniqueIDForThisGame'] = int(root.find('uniqueIDForThisGame').text)
    info['currentSeason'] = root.find('currentSeason').text
    # Collecting player stats
    info['stats'] = getStats(root)

    # Collecting pet name
    petTypes = ['Cat', 'Dog']
    petLocations = ['Farm', 'FarmHouse']
    try:
        info['petName'] = getNPCs(root, petLocations, petTypes)[0].find('name').text
    except IndexError:
        pass
    
    # Information for portrait generation
    p = {}
    partners = getPartners(root)
    if partners: 
        p['partner'] = partners[0].find('name').text
    else:
        p['partner'] = None
    p['cat']=strToBool(info['catPerson'])
    p['children'] = [(int(child.find('gender').text),strToBool(child.find('darkSkinned').text),int(child.find('daysOld').text),child.find('name').text) for child in getChildren(root)]

    info['portrait_info'] = json.dumps(p)
    info['animals'] = json.dumps(getAnimals(root))

    return info

def main():
    saveFile = "./saves/Lukas_117195717"
    p = player(saveFile)
    (p.getPlayerInfo())
    # print(p.getCurrentSeason())

if __name__ == '__main__':
    main()
