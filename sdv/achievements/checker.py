# adapted from

""" achievement_checker.py:
	Check a Stardew Valley save file for progress towards achievements.
	Author: Skatje Myers (sk@tjemye.rs)
	https://github.com/skatje-myers/stardewscripts """

# by Rob Heath rob@robheath.me.uk for SDV-Summary upload.farm
import json

fish_ids = {'153': 'Green Algae', '157': 'White Algae', '152': 'Seaweed', '372': 'Clam', '705': 'Albacore',
			'129': 'Anchovy', '160': 'Angler', '132': 'Bream', '700': 'Bullhead', '702': 'Bullhead', '142': 'Carp',
			'143': 'Catfish', '718': 'Cockle', '717': 'Crab', '716': 'Crayfish', '159': 'Crimsonfish',
			'704': 'Dorado', '148': 'Eel', '156': 'Ghostfish', '775': 'Glacierfish', '708': 'Halibut',
			'147': 'Herring', '161': 'Ice Pip', '137': 'Largemouth Bass', '162': 'Lava Eel', '163': 'Legend',
			'707': 'Lingcod', '715': 'Lobster', '719': 'Mussel', '682': 'Mutant Carp', '149': 'Octopus',
			'723': 'Oyster', '141': 'Perch', '722': 'Periwinkle', '144': 'Pike', '128': 'Pufferfish',
			'138': 'Rainbow Trout', '146': 'Red Mullet', '150': 'Red Snapper', '139': 'Salmon', '164': 'Sandfish',
			'131': 'Sardine', '165': 'Scorpion Carp', '154': 'Sea Cucumber', '706': 'Shad', '720': 'Shrimp',
			'136': 'Smallmouth Bass', '721': 'Snail', '151': 'Squid', '158': 'Stonefish', '698': 'Sturgeon',
			'145': 'Sunfish', '155': 'Super Cucumber', '699': 'Tiger Trout', '701': 'Tilapia', '130': 'Tuna',
			'140': 'Walleye', '734': 'Woodskip'}

recipe_ids = {'226': 'Spicy Eel', '218': 'Tom Kha Soup', '456': 'Algae Soup', '605': 'Artichoke Dip',
			  '235': 'Autumn\'s Bounty', '198': 'Baked Fish', '207': 'Bean Hotpot', '611': 'Blackberry Cobbler',
			  '234': 'Blueberry Tart', '216': 'Bread', '618': 'Bruschetta', '209': 'Carp Surprise',
			  '197': 'Cheese Cauliflower', '220': 'Chocolate Cake', '727': 'Chowder', '648': 'Coleslaw',
			  '201': 'Complete Breakfast', '223': 'Cookie', '732': 'Crab Cakes', '612': 'Cranberry Candy',
			  '238': 'Cranberry Sauce', '214': 'Crispy Bass', '242': 'Dish O\' The Sea', '231': 'Eggplant Parmesan',
			  '729': 'Escargot', '240': 'Farmer\'s Lunch', '649': 'Fiddlehead Risotto', '728': 'Fish Stew',
			  '213': 'Fish Taco', '202': 'Fried Calamari', '225': 'Fried Eel', '194': 'Fried Egg',
			  '205': 'Fried Mushroom', '610': 'Fruit Salad', '208': 'Glazed Yams', '210': 'Hashbrowns',
			  '233': 'Ice Cream', '730': 'Lobster Bisque', '204': 'Lucky Lunch', '228': 'Maki Roll',
			  '731': 'Maple Bar', '243': 'Miner\'s Treat', '195': 'Omelet', '457': 'Pale Broth', '211': 'Pancakes',
			  '199': 'Parsnip Soup', '215': 'Pepper Poppers', '221': 'Pink Cake', '206': 'Pizza',
			  '604': 'Plum Pudding', '651': 'Poppyseed Muffin', '608': 'Pumpkin Pie', '236': 'Pumpkin Soup',
			  '609': 'Radish Salad', '230': 'Red Plate', '222': 'Rhubarb Pie', '232': 'Rice Pudding',
			  '607': 'Roasted Hazelnuts', '244': 'Roots Platter', '196': 'Salad', '212': 'Salmon Dinner',
			  '227': 'Sashimi', '224': 'Spaghetti', '606': 'Stir Fry', '203': 'Strange Bun', '239': 'Stuffing',
			  '237': 'Super Meal', '241': 'Survival Burger', '480': 'Tomato Seeds', '229': 'Tortilla',
			  '219': 'Trout Soup', '200': 'Vegetable Medley'}

craftable_items = {'Bomb', 'Cherry Bomb', 'Crab Pot', 'Explosive Ammo', 'Field Snack', 'Gate', 'Hardwood Fence', 'Iridium Sprinkler', 'Iron Fence', 'Jack-O-Lantern', 'Mega Bomb', 'Quality Sprinkler', 'Sprinkler', 'Stone Fence', 'Torch', 'Wood Fence', 'Cobblestone Path', 'Crystal Floor', 'Crystal Path', 'Drum Block', 'Flute Block', 'Gravel Path', 'Stepping Stone Path', 'Stone Floor', 'Straw Floor', 'Weathered Floor', 'Wood Floor', 'Wood Path', 'Basic Fertilizer', 'Basic Retaining Soil', 'Deluxe Speed-Gro', 'Quality Fertilizer', 'Quality Retaining Soil', 'Bee House', 'Oil Maker', 'Preserves Jar', 'Staircase', 'Loom', 'Mayonnaise Machine', 'Seed Maker', 'Transmute (Fe)', 'Cheese Press', 'Scarecrow', 'Furnace', 'Chest', 'Tapper', 'Keg', 'Rain Totem', 'Wild Seeds (Fa)', 'Marble Brazier', 'Iridium Band', 'Life Elixir', 'Trap Bobber', 'Slime Incubator', 'Sturdy Ring', 'Dressed Spinner', 'Lightning Rod', 'Speed-Gro', 'Wooden Brazier', 'Wood Lamp-post', 'Bait', 'Campfire', "Tub o' Flowers", 'Iron Lamp-post', 'Stump Brazier', 'Slime Egg-Press', 'Wild Seeds (Wi)', 'Ring of Yoba', 'Transmute (Au)', 'Skull Brazier', 'Wild Seeds (Su)', 'Crystalarium', 'Warp Totem: Mountains', 'Barbed Hook', 'Carved Brazier', 'Magnet', 'Worm Bin', 'Stone Brazier', 'Oil Of Garlic', 'Cork Bobber', 'Recycling Machine', 'Charcoal Kiln', 'Spinner', 'Wild Seeds (Sp)', 'Gold Brazier', 'Barrel Brazier', 'Warrior Ring', 'Ancient Seeds', 'Treasure Hunter', 'Warp Totem: Beach', 'Wicked Statue', 'Warp Totem: Farm', 'Wild Bait'}

museum_ids = {'541': 'Aerinite', '538': 'Alamite', '66': 'Amethyst', '62': 'Aquamarine', '540': 'Baryte',
			  '570': 'Basalt', '539': 'Bixite', '542': 'Calcite', '566': 'Celestine', '72': 'Diamond',
			  '543': 'Dolomite', '86': 'Earth Crystal', '60': 'Emerald', '544': 'Esperite', '577': 'Fairy Stone',
			  '565': 'Fire Opal', '82': 'Fire Quartz', '545': 'Fluorapatite', '84': 'Frozen Tear',
			  '546': 'Geminite', '561': 'Ghost Crystal', '569': 'Granite', '547': 'Helvite', '573': 'Hematite',
			  '70': 'Jade', '549': 'Jagoite', '548': 'Jamborite', '563': 'Jasper', '550': 'Kyanite',
			  '554': 'Lemon Stone', '571': 'Limestone', '551': 'Lunarite', '552': 'Malachite', '567': 'Marble',
			  '574': 'Mudstone', '555': 'Nekoite', '553': 'Neptunite', '575': 'Obsidian', '560': 'Ocean Stone',
			  '564': 'Opal', '556': 'Orpiment', '557': 'Petrified Slime', '74': 'Prismatic Shard', '559': 'Pyrite',
			  '80': 'Quartz', '64': 'Ruby', '568': 'Sandstone', '576': 'Slate', '572': 'Soapstone',
			  '578': 'Star Shards', '558': 'Thunder Egg', '562': 'Tigerseye', '68': 'Topaz',
			  '587': 'Amphibian Fossil', '117': 'Anchor', '103': 'Ancient Doll', '123': 'Ancient Drum',
			  '114': 'Ancient Seed', '109': 'Ancient Sword', '101': 'Arrowhead', '119': 'Bone Flute',
			  '105': 'Chewing Stick', '113': 'Chicken Statue', '100': 'Chipped Amphora', '107': 'Dinosaur Egg',
			  '116': 'Dried Starfish', '122': 'Dwarf Gadget', '96': 'Dwarf Scroll I', '97': 'Dwarf Scroll II',
			  '98': 'Dwarf Scroll III', '99': 'Dwarf Scroll IV', '121': 'Dwarvish Helm', '104': 'Elvish Jewelry',
			  '118': 'Glass Shards', '124': 'Golden Mask', '125': 'Golden Relic', '586': 'Nautilus Shell',
			  '106': 'Ornamental Fan', '588': 'Palm Fossil', '120': 'Prehistoric Handaxe', '583': 'Prehistoric Rib',
			  '579': 'Prehistoric Scapula', '581': 'Prehistoric Skull', '580': 'Prehistoric Tibia',
			  '115': 'Prehistoric Tool', '584': 'Prehistoric Vertebra', '108': 'Rare Disc', '112': 'Rusty Cog',
			  '110': 'Rusty Spoon', '111': 'Rusty Spur', '582': 'Skeletal Hand', '585': 'Skeletal Tail',
			  '126': 'Strange Doll', '127': 'Strange Doll', '589': 'Trilobite'}

shipping_ids = {'300': 'Amaranth', '274': 'Artichoke', '284': 'Beet', '278': 'Bok Choy', '190': 'Cauliflower',
				'270': 'Corn', '272': 'Eggplant', '259': 'Fiddlehead Fern', '248': 'Garlic', '188': 'Green Bean',
				'304': 'Hops', '250': 'Kale', '24': 'Parsnip', '192': 'Potato', '276': 'Pumpkin', '264': 'Radish',
				'266': 'Red Cabbage', '262': 'Wheat', '280': 'Yam', '442': 'Duck Egg', '444': 'Duck Feather',
				'176': 'Egg (white)', '180': 'Egg (brown)', '436': 'Goat Milk', '438': 'L. Goat Milk',
				'174': 'Large Egg', '182': 'Large Egg', '186': 'Large Milk', '184': 'Milk', '446': 'Rabbit\'s Foot',
				'305': 'Void Egg', '440': 'Wool', '346': 'Beer', '424': 'Cheese', '428': 'Cloth',
				'307': 'Duck Mayonnaise', '426': 'Goat Cheese', '340': 'Honey', '344': 'Jelly', '350': 'Juice',
				'724': 'Maple Syrup', '306': 'Mayonnaise', '725': 'Oak Resin', '303': 'Pale Ale', '342': 'Pickles',
				'726': 'Pine Tar', '432': 'Truffle Oil', '348': 'Wine', '597': 'Blue Jazz', '418': 'Crocus',
				'595': 'Fairy Rose', '376': 'Poppy', '593': 'Summer Spangle', '421': 'Sunflower',
				'402': 'Sweet Pea', '591': 'Tulip', '78': 'Cave Carrot', '281': 'Chanterelle',
				'404': 'Common Mushroom', '393': 'Coral', '18': 'Daffodil', '22': 'Dandelion', '408': 'Hazelnut',
				'283': 'Holly', '20': 'Leek', '257': 'Morel', '422': 'Purple Mushroom', '394': 'Rainbow Shell',
				'420': 'Red Mushroom', '92': 'Sap', '397': 'Sea Urchin', '416': 'Snow Yam', '399': 'Spring Onion',
				'430': 'Truffle', '16': 'Wild Horseradish', '406': 'Wild Plum', '412': 'Winter Root',
				'613': 'Apple', '634': 'Apricot', '410': 'Blackberry', '258': 'Blueberry', '90': 'Cactus Fruit',
				'638': 'Cherry', '88': 'Coconut', '282': 'Cranberries', '414': 'Crystal Fruit', '398': 'Grape',
				'260': 'Hot Pepper', '254': 'Melon', '635': 'Orange', '636': 'Peach', '637': 'Pomegranate',
				'252': 'Rhubarb', '296': 'Salmonberry', '268': 'Starfruit', '400': 'Strawberry',
				'417': 'Sweet Gem Berry', '787': 'Battery Pack', '330': 'Clay', '382': 'Coal', '334': 'Copper Bar',
				'378': 'Copper Ore', '771': 'Fiber', '336': 'Gold Bar', '384': 'Gold Ore', '709': 'Hardwood',
				'337': 'Iridium Bar', '386': 'Iridium Ore', '335': 'Iron Bar', '380': 'Iron Ore',
				'338': 'Refined Quartz', '390': 'Stone', '388': 'Wood', '392': 'Nautilus Shell'}

crop_ids = {'300': 'Amaranth', '274': 'Artichoke', '188': 'Green Bean', '284': 'Beet', '258': 'Blueberry',
			'278': 'Bok Choy', '190': 'Cauliflower', '270': 'Corn', '282': 'Cranberries', '272': 'Eggplant',
			'595': 'Fairy Rose', '248': 'Garlic', '398': 'Grape', '304': 'Hops', '597': 'Blue Jazz', '250': 'Kale',
			'254': 'Melon', '24': 'Parsnip', '260': 'Hot Pepper', '376': 'Poppy', '192': 'Potato', '276': 'Pumpkin',
			'264': 'Radish', '266': 'Red Cabbage', '252': 'Rhubarb', '593': 'Summer Spangle', '268': 'Starfruit',
			'400': 'Strawberry', '421': 'Sunflower', '417': 'Sweet Gem Berry', '256': 'Tomato', '591': 'Tulip',
			'262': 'Wheat', '280': 'Yam'}

def main(datadict,friendships):
	missing_achievements = {}

	missing_achievements['Money'] = []
	earned = int(datadict['totalMoneyEarned'])
	for threshold in [10000000,1000000,250000,50000,15000]:
		if earned < threshold:
			missing_achievements['Money'].append(threshold)

	missing_achievements['Friendship'] = []
	num_5 = 0
	num_10 = 0
	for friendship in friendships:
		points = friendship[1]
		if points >= 2500:
			num_10 += 1
		if points >= 1250:
			num_5 += 1
	if num_10 < 8:
		if num_5 < 20:
			missing_achievements['Friendship'].append('5-heart friendship with 20 people')
			if num_5 < 10:
				missing_achievements['Friendship'].append('5-heart friendship with 10 people')
				if num_5 == 0:
					missing_achievements['Friendship'].append('5-heart friendship with 1 person')
		missing_achievements['Friendship'].append('10-heart friendship with 8 people')
		if num_10 == 0:
			missing_achievements['Friendship'].append('10-heart friendship with 1 person')

	missing_achievements['Fish'] = []
	try:
		fish = json.loads(datadict['fish_json'])
		num_caught = sum(fish.values())
		caught_ids = set(fish.keys())
		if num_caught < 100:
			missing_achievements['Fish'].append('Catch 100 fish')
		if len(caught_ids) < len(fish_ids.keys()):
			missing_achievements['Fish'].append('Catch all types of fish')
			if len(caught_ids) < 24:
				missing_achievements['Fish'].append('Catch 24 different types of fish')
				if len(caught_ids) < 10:
					missing_achievements['Fish'].append('Catch 10 different types of fish')
			missing = {'missing':[fish_ids[id] for id in list(set(fish_ids.keys()) - caught_ids)]}
			missing_achievements['Fish'].append(missing)
	except TypeError:
		pass

	missing_achievements['Recipes'] = []
	try:
		recipes = json.loads(datadict['recipes_json'])
		known_recipes = set(recipes['known'])
		cooked_recipes = set(recipes['cooked'])
		if len(cooked_recipes) < len(recipe_ids.keys()):
			missing_achievements['Recipes'].append('Cook all recipes')
			if len(cooked_recipes) < 25:
				missing_achievements['Recipes'].append('Cook 25 different recipes')
				if len(cooked_recipes) < 10:
					missing_achievements['Recipes'].append('Cook 10 different recipes')
			missing = set(recipe_ids.keys()) - cooked_recipes
			missing = set(recipe_ids[id] for id in missing)
			unknown_missing = missing - known_recipes
			known_missing = list(missing - unknown_missing)
			unknown_missing = list(unknown_missing)
			if len(known_missing) > 0:
				missing_achievements['Recipes'].append({'missing-known':known_missing})
			if len(unknown_missing) > 0:
				missing_achievements['Recipes'].append({'missing-unknown':unknown_missing})
	except TypeError:
		pass

	missing_achievements['Craftables'] = []
	try:
		craftables = json.loads(datadict['craftables_json'])
		crafted = set(craftables['crafted'].keys())
		known_recipes = set(craftables['known'])

		if len(crafted) < len(craftable_items):
			missing_achievements['Craftables'].append('Craft all items')
			if len(crafted) < 30:
				missing_achievements['Craftables'].append('Craft 30 different items')
				if len(crafted) < 15:
					missing_achievements['Craftables'].append('Craft 15 different items')

			missing = craftable_items - crafted
			unknown_missing = missing - known_recipes
			known_missing = list(missing - unknown_missing)
			unknown_missing = list(unknown_missing)
			if len(known_missing) > 0:
				missing_achievements['Craftables'].append({'missing-known':known_missing})
			if len(unknown_missing) > 0:
				missing_achievements['Craftables'].append({'missing-unknown':unknown_missing})
	except TypeError:
		pass

	missing_achievements['Museum'] = []
	try:
		museum = json.loads(datadict['museum_json'])
		donated = set(museum)
		if len(set(museum_ids.keys()) - donated) > 0:
			missing_achievements['Museum'].append('Complete the museum collection')
			if len(donated) < 40:
				missing_achievements['Museum'].append('Donate 40 items to the museum')
			missing = list(set(museum_ids.keys()) - donated)
			missing = [museum_ids[id] for id in missing]
			missing_achievements['Museum'].append({'missing':missing})
	except TypeError:
		pass

	missing_achievements['Quests'] = []
	try:
		num_quests = int(datadict['statsQuestsCompleted'])
		if num_quests < 40:
			missing_achievements['Quests'].append('Do 40 quests')
			if num_quests < 10:
				missing_achievements['Quests'].append('Do 10 quests')
	except TypeError:
		pass

	missing_achievements['Shipping'] = []
	try:
		shipping = json.loads(datadict['shipping_json'])
		shipped = shipping['all']
		shipped_crops = shipping['crops']
		if len(set(shipping_ids.keys()) - set(shipped.keys())) > 0:
			missing_achievements['Shipping'].append('Ship every item')
			missing = list(set(shipping_ids.keys()) - set(shipped.keys()))
			missing = [shipping_ids[id] for id in missing]
			missing_achievements['Shipping'].append({'missing-all':missing})

			missing = []
			for crop in list(crop_ids):
				try:
					if shipped_crops[crop] < 15:
						missing.append(crop_ids[crop])
				except KeyError:
					missing.append(crop_ids[crop])
			if len(missing) > 0:
				missing_achievements['Shipping'].append('Ship 15 of every crop')
				missing_achievements['Shipping'].append({'missing-crops':missing})
			if len(shipped_crops) > 0:
				max_shipped = max(shipped_crops, key=shipped_crops.get)
				if shipped_crops[max_shipped] < 300:
					missing_achievements['Shipping'].append('Ship 300 of one crop')
					missing_achievements['Shipping'].append({'missing-max':{'type':crop_ids[max_shipped],'number':shipped_crops[max_shipped]}})
			else:
				missing_achievements['Shipping'].append('Ship 300 of one crop')
	except TypeError:
		pass

	missing_achievements['Skills'] = []
	skill_exp = dict()
	skill_exp['Farming'] = datadict['farmingLevel']
	skill_exp['Mining'] = datadict['miningLevel']
	skill_exp['Foraging'] = datadict['foragingLevel']
	skill_exp['Fishing'] = datadict['fishingLevel']
	skill_exp['Combat'] = datadict['combatLevel']

	max_skill = max(skill_exp, key=skill_exp.get)
	min_skill = min(skill_exp, key=skill_exp.get)
	if skill_exp[max_skill] < 15000:
		missing_achievements['Skills'].append('Level 10 in a skill')
	if skill_exp[min_skill] < 15000:
		missing_achievements['Skills'].append('Level 10 in every skill')
		missing = []
		for skill in skill_exp:
			if skill_exp[skill] < 15000:
				missing.append([skill,str(skill_exp[skill]) + '/15000'])
		missing_achievements['Skills'].append({'missing':missing})

	## Mining
	missing_achievements['Other'] = []
	if datadict['deepestMineLevel'] < 100:
		missing_achievements['Other'].append('Reach level 100 in the mines')

	def nz(value):
		if value == None:
			return 0
		else:
			return value

	## Protector of the Valley
	slime = nz(datadict['statsSlimesKilled']) + nz(datadict['statsSpecificMonstersKilledSludge']) + nz(datadict['statsSpecificMonstersKilledFrost_Jelly'])
	void = nz(datadict['statsSpecificMonstersKilledShadow_Brute']) + nz(datadict['statsSpecificMonstersKilledShadow_Shaman'])
	bat =  nz(datadict['statsSpecificMonstersKilledBat']) + nz(datadict['statsSpecificMonstersKilledFrost_Bat']) + nz(datadict['statsSpecificMonstersKilledLava_Bat'])
	skeleton = nz(datadict['statsSpecificMonstersKilledSkeleton'])
	bug =  nz(datadict['statsSpecificMonstersKilledBug']) + nz(datadict['statsSpecificMonstersKilledFly']) + nz(datadict['statsSpecificMonstersKilledGrub'])
	duggy = nz(datadict['statsSpecificMonstersKilledDuggy'])
	dust = nz(datadict['statsSpecificMonstersKilledDust_Spirit'])

	if slime < 1000 or void < 150 or bat < 200 or skeleton < 50 or bug < 125 or duggy < 30 or dust < 500:
		missing_achievements['Other'].append({'monster':['Complete Adventue Guild Monster Slayer goals']})
		missing = []
		if slime < 1000:
			missing.append({'slime':str(slime) + '/1000'})
		if void < 150:
			missing.append({'void':str(void) + '/150'})
		if bat < 200:
			missing.append({'bat':str(bat) + '/200'})
		if skeleton < 50:
			missing.append({'skeleton':str(skeleton) + '/50'})
		if bug < 125:
			missing.append({'bug':str(bug) + '/125'})
		if duggy < 30:
			missing.append({'duggy':str(duggy) + '/30'})
		if dust < 500:
			missing.append({'dust':str(dust) + '/500'})
		missing_achievements['Other'][-1]['monster']+= missing

	return missing_achievements

	## Fullhouse
	kids = 0
	npcs = root.find('locations').find('GameLocation').find('characters').findall('NPC')
	for npc in npcs:
		if npc.get('{http://www.w3.org/2001/XMLSchema-instance}type') == 'Child':
			kids += 1
	if kids < 2:
		print(RED + '\t*** Spouse and two children ***' + END)

	## Community Center
	locations = root.find('locations').findall('GameLocation')
	for location in locations:
		if location.get('{http://www.w3.org/2001/XMLSchema-instance}type') == 'CommunityCenter':
			for bool in location.find('areasComplete').findall('boolean'):
				if bool.text == 'false':
					print(RED + '\t*** Complete all community center bundles. ***' + END)
					break


	## Joja Mart


	## Stardrops

	## Prairie King
	# Beat prairie king
	# beat prairie king without dying
