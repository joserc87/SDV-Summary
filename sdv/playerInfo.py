import json
from sdv import validate
from sdv.savefile import get_location

ns = "{http://www.w3.org/2001/XMLSchema-instance}"
animal_habitable_buildings = ['Coop', 'Barn', 'SlimeHutch']
playerTags = ['name', 'isMale', 'farmName', 'favoriteThing', 'catPerson', 'deepestMineLevel', 'farmingLevel',
            'miningLevel', 'combatLevel', 'foragingLevel', 'fishingLevel', 'professions', 'maxHealth', 'maxStamina',
            'maxItems', 'money', 'totalMoneyEarned', 'millisecondsPlayed', 'friendships', 'shirt', 'hair', 'skin',
            'accessory', 'facialHair', 'hairstyleColor', 'pantsColor', 'newEyeColor','dayOfMonthForSaveGame','seasonForSaveGame','yearForSaveGame']
            # 'dateStringForSaveGame' removed
professions = ['Rancher', 'Tiller', 'Coopmaster', 'Shepherd', 'Artisan', 'Agriculturist', 'Fisher', 'Trapper',
            'Angler', 'Pirate', 'Mariner', 'Luremaster', 'Forester', 'Gatherer', 'Lumberjack', 'Tapper', 'Botanist',
            'Tracker','Miner', 'Geologist', 'Blacksmith', 'Prospector', 'Excavator', 'Gemologist', 'Fighter', 'Scout',
            'Brute', 'Defender','Acrobat', 'Desperado']
petTypes = ['Cat', 'Dog']
petLocations = ['Farm', 'FarmHouse']

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


# def getPartners(root):
#     partners = []
#     for location in root.find('locations').iter('GameLocation'):
#         for npc in location.iter('NPC'):
#             if int(npc.find('daysMarried').text) > 0:
#                 partners.append(npc)
#     return partners


def getPartners(rpof):
    # rpof = "root, player, or farmhand" - indicates the variable can be any one of these three (depending on the save version)

    # player = root.find("player")
    try:
        if rpof.find("spouse").text:
            partner = rpof.find("spouse").text
            if partner in validate.marriage_candidates:
                return partner
    except AttributeError:
        pass
    return None


def getChildren(rpof):
    children = []
    childType = ['Child']
    childLocation = ['Farm', 'FarmHouse']
    child_nodes = getNPCs(rpof, childLocation, childType)
    return child_nodes


def getStats(rpof):
    game_stats = {}

    stats_node = rpof.find('stats')

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
    farm_location = get_location(root,'Farm')
    animals = {}
    for item in farm_location.find('buildings').iter('Building'):
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

def v1_3(root):
    try:
        v1_3 = True if strToBool(root.find('hasApplied1_3_UpdateChanges').text) else False
    except:
        v1_3 = False
    return v1_3

def playerInfo(saveFile):
    root = saveFile.getRoot()

    if v1_3(root):
        players = [root.find('player')]
        for value in root.iter('farmhand'):
            if value.find('name').text:
                players.append(value)
    else:
        players = [root]

    player_children = getChildren(root)
    info = get_player_or_farmhand_info(players[0],v1_3,player_children)

    # Information from elsewhere
    # UID for save file
    info['uniqueIDForThisGame'] = int(root.find('uniqueIDForThisGame').text)

    season = root.find('currentSeason').text
    assert season in validate.seasons
    info['currentSeason'] = season

    # Collecting pet name
    try:
        info['petName'] = getNPCs(root, petLocations, petTypes)[0].find('name').text
    except IndexError:
        pass

    info['animals'] = json.dumps(getAnimals(root))

    if len(players) > 1:
        info['farmhands'] = {}
        for farmhand in players[1:]:
            info['farmhands'][farmhand.find('name').text] = get_player_or_farmhand_info(farmhand,v1_3,player_children)

    # print(info)

    return info

def get_player_or_farmhand_info(node,v1_3,player_children=[]):
    # Collect information stored in the player tag
    child_names = [c.find('name').text for c in player_children]
    info = {}
    for tag in playerTags:
        try:
            if node.find(tag).text != None:
                s = node.find(tag).text
            else:
                if tag == "professions":
                    profs = node.find(tag)
                    s = []
                    for a in profs.iter("int"):
                        a = int(a.text)
                        if a < len(professions) and len(s) < 10:
                            s.append(professions[a])
                if tag == "friendships":
                    s = {}
                    if v1_3:
                        fship = node.find("friendshipData")
                    else:
                        fship = node.find(tag)
                    for item in fship:
                        name = item.find("key").find('string').text
                        if name not in child_names:
                            if name in validate.giftable_npcs:
                                rating = int(item.find('value').find('ArrayOfInt').find('int').text)
                                assert rating >= 0 and rating < 14*250
                                s[name] = rating

                if tag in ['hairstyleColor', 'pantsColor', 'newEyeColor']:
                    red = int(node.find(tag).find('R').text)
                    assert red >= 0 and red <= 255

                    green = int(node.find(tag).find('G').text)
                    assert green >= 0 and green <= 255

                    blue = int(node.find(tag).find('B').text)
                    assert blue >= 0 and blue <= 255

                    alpha = int(node.find(tag).find('A').text)
                    assert alpha >= 0 and alpha <= 255

                    s = [red, green, blue, alpha]

            if tag in ['name', 'farmName', 'favoriteThing']:
                assert len(tag) <= 32
            # if tag == 'dateStringForSaveGame':
            #     tag = 'date'
            info[tag] = s
        except AttributeError:
            pass

    # Collecting player stats
    info['stats'] = getStats(node)

    p = {}
    # Information for portrait generation
    p['partner'] = getPartners(node) #returns the name of the partner, nothing else
    p['cat'] = strToBool(info['catPerson']) #true or false
    #children is a problem though. because it doesn't identify parenthood.
    p['children'] = [(int(child.find('gender').text), strToBool(child.find('darkSkinned').text),int(child.find('daysOld').text),child.find('name').text) for child in player_children]
    info['portrait_info'] = json.dumps(p)

    return info


def main():
    saveFile = savefile.savefile("./OneDotThree_184790837")
    p = player(saveFile)
    (p.getPlayerInfo())

if __name__ == '__main__':
    main()
