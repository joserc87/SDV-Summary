import json
from sdv import validate
import sdv.savefile

ns = "{http://www.w3.org/2001/XMLSchema-instance}"
animal_habitable_buildings = ['Coop', 'Barn', 'SlimeHutch']


class player:
    """docstring for player"""
    def __init__(self, saveFile):
        # super(player, self).__init__()
        self.saveFile = saveFile
        self.root = self.saveFile.getRoot()

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


def playerInfo(saveFile):
    playerTags = ['name', 'isMale', 'farmName', 'favoriteThing', 'catPerson', 'deepestMineLevel', 'farmingLevel',
                'miningLevel', 'combatLevel', 'foragingLevel', 'fishingLevel', 'professions', 'maxHealth', 'maxStamina',
                'maxItems', 'money', 'totalMoneyEarned', 'millisecondsPlayed', 'friendships', 'shirt', 'hair', 'skin',
                'accessory', 'facialHair', 'hairstyleColor', 'pantsColor', 'newEyeColor','dateStringForSaveGame']
    professions = ['Rancher', 'Tiller', 'Coopmaster', 'Shepherd', 'Artisan', 'Agriculturist', 'Fisher', 'Trapper',
                'Angler', 'Pirate', 'Mariner', 'Luremaster', 'Forester', 'Gatherer', 'Lumberjack', 'Tapper', 'Botanist',
                'Tracker','Miner', 'Geologist', 'Blacksmith', 'Prospector', 'Excavator', 'Gemologist', 'Fighter', 'Scout',
                'Brute', 'Defender','Acrobat', 'Desperado']
    root = saveFile.getRoot()

    player = root.find("player")
    player_children = getChildren(root)
    child_names = [c.find('name').text for c in player_children]
    info = {}

    # Collect information stored in the player tag
    for tag in playerTags:
        if player.find(tag).text != None:
            s = player.find(tag).text
        else:
            if tag == "professions":
                profs = player.find(tag)
                s = []
                for a in profs.iter("int"):
                    a = int(a.text)
                    if a < len(professions):
                        s.append(professions[a])
            if tag == "friendships":
                s = {}
                fship = player.find(tag)
                for item in fship:
                    name = item.find("key").find('string').text
                    if name not in child_names:
                        if name in validate.giftable_npcs:
                            rating = int(item.find('value').find('ArrayOfInt').find('int').text)
                            assert rating >= 0 and rating < 14*250
                            s[name] = rating

            if tag in ['hairstyleColor', 'pantsColor', 'newEyeColor']:
                red = int(player.find(tag).find('R').text)
                assert red >= 0 and red <= 255

                green = int(player.find(tag).find('G').text)
                assert green >= 0 and green <= 255

                blue = int(player.find(tag).find('B').text)
                assert blue >= 0 and blue <= 255

                alpha = int(player.find(tag).find('A').text)
                assert alpha >= 0 and alpha <= 255

                s = [red, green, blue, alpha]

        if tag in ['name', 'farmName', 'favoriteThing']:
            assert len(tag) <= 32
        if tag == 'dateStringForSaveGame':
            tag = 'date'
        info[tag] = s

    # Information from elsewhere
    # UID for save file
    info['uniqueIDForThisGame'] = int(root.find('uniqueIDForThisGame').text)

    season = root.find('currentSeason').text
    assert season in validate.seasons
    info['currentSeason'] = season

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
        partner_name = partners[0].find('name').text
        print(partner_name)
        assert partner_name in validate.marriage_candidates
        p['partner'] = partner_name
    else:
        p['partner'] = None
    p['cat'] = strToBool(info['catPerson'])
    p['children'] = [(int(child.find('gender').text), strToBool(child.find('darkSkinned').text),int(child.find('daysOld').text),child.find('name').text) for child in player_children]

    info['portrait_info'] = json.dumps(p)
    info['animals'] = json.dumps(getAnimals(root))

    return info


def main():
    saveFile = savefile.savefile("./saves/Kristi_119549314")
    p = player(saveFile)
    (p.getPlayerInfo())

if __name__ == '__main__':
    main()
