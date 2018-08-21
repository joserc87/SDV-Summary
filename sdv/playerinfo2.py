import json
from sdv import validate
from sdv.savefile import get_location

ns = "{http://www.w3.org/2001/XMLSchema-instance}"

animal_habitable_buildings = ['Coop', 'Barn', 'SlimeHutch']

# 'dateStringForSaveGame' removed
playerTags = ['name', 'UniqueMultiplayerID', 'isMale', 'farmName', 'favoriteThing', 'catPerson',
              'deepestMineLevel', 'farmingLevel', 'miningLevel', 'combatLevel', 'foragingLevel',
              'fishingLevel', 'professions', 'maxHealth', 'maxStamina', 'maxItems', 'money',
              'totalMoneyEarned', 'millisecondsPlayed', 'friendships', 'shirt', 'hair', 'skin',
              'accessory', 'facialHair', 'hairstyleColor', 'pantsColor', 'newEyeColor',
              'dayOfMonthForSaveGame', 'seasonForSaveGame', 'yearForSaveGame']

professions = ['Rancher', 'Tiller', 'Coopmaster', 'Shepherd', 'Artisan', 'Agriculturist', 'Fisher',
               'Trapper', 'Angler', 'Pirate', 'Mariner', 'Luremaster', 'Forester', 'Gatherer',
               'Lumberjack', 'Tapper', 'Botanist', 'Tracker', 'Miner', 'Geologist', 'Blacksmith',
               'Prospector', 'Excavator', 'Gemologist', 'Fighter', 'Scout', 'Brute', 'Defender',
               'Acrobat', 'Desperado']

petTypes = ['Cat', 'Dog']

petLocations = ['Farm', 'FarmHouse']

childType = ['Child']

childLocation = ['Farm', 'FarmHouse']


def str_to_bool(x):
    return x.lower() == 'true'


def get_animals(farm, get_npcs):
    animals = {}
    for building in farm.find('buildings').iter('Building'):
        buildingtype = building.get(ns + 'type')
        name = building.find('buildingType').text
        if buildingtype in animal_habitable_buildings:
            for animal in building.find('indoors').find('animals').iter('item'):
                animal = animal.find('value').find('FarmAnimal')
                an = animal.find('name').text
                aa = int(animal.find('age').text)
                at = animal.find('type').text
                ah = int(animal.find('happiness').text)
                ahx = int(animal.find('homeLocation').find('X').text)
                ahy = int(animal.find('homeLocation').find('Y').text)
                animaltuple = (an, aa, ah, ahx, ahy, name)
                try:
                    animals[at].append(animaltuple)
                except KeyError:
                    animals[at] = [animaltuple]
    horse = get_npcs(['Farm'], ['Horse'])
    if horse != []:
        animals['horse'] = horse[0].find('name').text
    return animals


class GameInfo:
    def __init__(self, element_tree):
        super().__init__()
        self.element_tree = element_tree
        self.root = self.element_tree.getRoot()
        self.get_players()
        self.get_animals()
        self.get_children()

        self.get_info()

    def get_info(self):
        if not hasattr(self, 'info'):
            self.info = self.player.get_info()

            self.info['uniqueIDForThisGame'] = int(self.root.find('uniqueIDForThisGame').text)

            self.current_season = self.root.find('currentSeason').text
            assert self.current_season in validate.seasons
            self.info['currentSeason'] = self.current_season

            try:
                self.info['petName'] = self._get_npcs(petLocations, petTypes)[0].find('name').text
            except IndexError:
                pass

            self.info['animals'] = json.dumps(self.get_animals())

            if len(self.farmhands) > 0:
                self.info['farmhands'] = []
                for farmhand in self.farmhands:
                    self.info['farmhands'].append(farmhand.get_info())

            players = [self.info]
            if self.info.get('farmhands'):
                players.extend(self.info.get('farmhands'))
            for player in players:
                player_json = json.loads(player['portrait_info'])
                partner_id = player_json.get('partner_id')
                if partner_id:
                    partner = next(
                        filter(lambda x: x.get('UniqueMultiplayerID') == partner_id, players)
                    )
                    player_json['partner'] = partner['name']
                    player['portrait_info'] = json.dumps(player_json)

        else:
            return self.info

    def get_children(self):
        if not hasattr(self, 'children'):
            self.children = self._get_npcs(childLocation, childType)
        return self.children

    def get_animals(self):
        if not hasattr(self, '_animals'):
            self._animals = get_animals(get_location(self.root, 'Farm'), self._get_npcs)
        return self._animals

    def _get_npcs(self, loc, types):
        self._npcs = []
        for location in self.root.find('locations').iter('GameLocation'):
            if location.get(ns + 'type') in loc:
                self._npc_temp = location.find('characters').iter('NPC')
                self._npcs += [npc for npc in self._npc_temp if npc.get(ns + 'type') in types]
        return self._npcs

    def v1_3(self):
        if not hasattr(self, '_v1_3'):
            try:
                self._v1_3 = True if str_to_bool(
                        self.root.find('hasApplied1_3_UpdateChanges').text) else False
            except:
                self._v1_3 = False
        return self._v1_3

    def get_players(self):
        if not hasattr(self, 'player') or not hasattr(self, 'farmhands'):
            self.farmhands = []
            if self.v1_3():
                self.player = Player(self.root.find('player'), self.get_children(), self.v1_3(),
                                     self.root.find('farmerFriendships'))
                for fh in self.root.iter('farmhand'):
                    if fh.find('name').text:
                        self.farmhands.append(Player(fh, self.get_children(), self.v1_3(),
                                                     self.root.find('farmerFriendships')))
            else:
                self.player = Player(self.root, self.get_children(), self.v1_3())
        return [self.player] + self.farmhands


class Player:
    def __init__(self, node, children, v1_3, farmer_friendships=None):
        super().__init__()
        self.node = node
        self.player_node = self.node if v1_3 else self.node.find('player')
        self.set_children(children)
        self.v1_3 = v1_3
        self.get_player_tags()
        self.farmer_friendships = farmer_friendships

    def get_player_tags(self):
        self.player_tags = list(playerTags)
        if self.v1_3:
            self.player_tags[self.player_tags.index("friendships")] = "friendshipData"

    def set_children(self, children):
        self.children = children
        self.child_names = [c.find('name').text for c in children]

    def get_info(self):
        if not hasattr(self, 'info'):
            self.info = {}
            for tag in self.player_tags:
                try:
                    if self.player_node.find(tag).text != None:
                        self.info[tag] = self.player_node.find(tag).text
                    else:
                        if tag == "professions":
                            self.info["professions"] = get_professions(self.player_node)
                        elif tag in ["friendships", "friendshipData"]:
                            self.info["friendships"] = get_friendships(self.player_node, self.v1_3)
                        elif tag in ['hairstyleColor', 'pantsColor', 'newEyeColor']:
                            self.info[tag] = list(map(
                                    lambda c: int(self.player_node.find(tag).find('R').text),
                                    'RGBA'
                            ))
                            assert all([0 <= i <= 255 for i in self.info[tag]])
                    # if tag in ['name', 'farmName', 'favoriteThing']:
                    #     assert len(tag) <= 32
                except AttributeError:
                    pass

            # Collecting player stats
            self.info['stats'] = get_stats(self.node)

            self._portrait_info = {}
            # Information for portrait generation
            self._portrait_info['partner'] = get_partner(self.player_node)
            if not self._portrait_info['partner'] and self.farmer_friendships:
                self._portrait_info['partner_id'] = get_multiplayer_partner(
                        self.info['UniqueMultiplayerID'],
                        self.farmer_friendships)
            self._portrait_info['cat'] = str_to_bool(self.info['catPerson'])
            # children is a problem though. because it doesn't identify parenthood.
            self._portrait_info['children'] = [(int(child.find('gender').text),
                                                str_to_bool(child.find('darkSkinned').text),
                                                int(child.find('daysOld').text),
                                                child.find('name').text) for child in self.children]
            self.info['portrait_info'] = json.dumps(self._portrait_info)
        return self.info


def get_professions(node):
    profs = node.find("professions")
    s = []
    for a in profs.iter("int"):
        a = int(a.text)
        if a < len(professions) and len(s) < 10:
            s.append(professions[a])
    return s


def get_friendships(node, v1_3):
    s = {}
    if v1_3:
        fship = node.find("friendshipData")
    else:
        fship = node.find("friendships")
    for item in fship:
        name = item.find("key").find('string').text
        if name in validate.giftable_npcs:
            if v1_3:
                rating = int(item.find('value').find('Friendship').find('Points').text)
            else:
                rating = int(item.find('value').find('ArrayOfInt').find('int').text)
            assert rating >= 0 and rating < 14 * 250
            s[name] = rating
    return s


def get_partner(node):
    try:
        if node.find("spouse").text:
            partner = node.find("spouse").text
            if partner in validate.marriage_candidates:
                return partner
    except AttributeError:
        pass
    return None


def get_multiplayer_partner(player_id, farmer_friendships):
    """
    Given a player ID check for multi-player spouses
    :param player_id: Unique ID for player
    :param farmer_friendships: XML node of multi-player friendships
    :return:
    """
    for item in farmer_friendships.iter('item'):
        farmer1 = next(item.iter('Farmer1')).text
        farmer2 = next(item.iter('Farmer2')).text
        status = next(item.iter('Status')).text
        if player_id in [farmer1, farmer2] and status == 'Married':
            return farmer1 if player_id != farmer1 else farmer2
    return None


def get_stats(node):
    game_stats = {}
    for statistic in node.find('stats'):
        stattag = statistic.tag[0].upper() + statistic.tag[1:]
        if stattag not in game_stats.keys():
            # check we're drawing info from the uppercase data and data not already exist
            if statistic.text != None:
                # print('node: {}'.format(node.find('name').text))
                # print('stattag: {}, text: {}'.format(stattag,statistic.text))
                game_stats[stattag] = int(statistic.text)
            elif stattag == 'SpecificMonstersKilled':
                monsters = {}
                for monster in statistic.iter('item'):
                    monsterName = monster.find('key').find('string').text
                    count = int(monster.find('value').find('int').text)
                    monsters[monsterName] = count
                game_stats[stattag] = monsters
    return game_stats


if __name__ == "__main__":
    p = GameInfo('filename')
    info = p.getPlayerInfo()
