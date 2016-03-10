#
# converts base 10 to base 62 for purpose of small URL identifiers
#

CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def dec2big(num):
	assert type(num) in [int,long]
	if num == 0:
		output = CHARS[0]
	elif num > 0:
		base = len(CHARS)
		output = ''
		while num > 0:
			rem = num%base
			output = CHARS[rem] + output
			num = (num-rem)/base
	else:
		raise IOError
	return output

def big2dec(num):
	assert all([num[x] in CHARS for x in range(len(num))])
	base = len(CHARS)
	output = 0
	multiplier = 1
	for item in num[::-1]:
		output += multiplier * CHARS.index(item)
		multiplier *= base
	return output


if __name__ == "__main__":
	print dec2big(9999999999999999999999999999999999999999999999999999999)
	print big2dec('gUFRx61gTwUoLRUcYcoUr2SbzgUyBQz')

	sketchy = ['url', 'isMale', 'pantsColor0', 'pantsColor1', 'pantsColor2', 'pantsColor3', 'combatLevel', 'maxHealth', 'hair', 'favoriteThing', 'maxItems', 'skin', 'friendshipsWilly', 'friendshipsClint', 'friendshipsJodi', 'friendshipsHarvey', 'friendshipsLeah', 'friendshipsWizard', 'friendshipsJas', 'friendshipsAbigail', 'friendshipsMaru', 'friendshipsElliott', 'friendshipsCaroline', 'friendshipsPam', 'friendshipsDwarf', 'friendshipsShane', 'friendshipsDemetrius', 'friendshipsAlex', 'friendshipsGus', 'friendshipsVincent', 'friendshipsSebastian', 'friendshipsRobin','friendshipsSam', 'friendshipsLewis', 'friendshipsMarnie', 'friendshipsPenny', 'friendshipsHaley', 'friendshipsPierre', 'friendshipsEvelyn', 'friendshipsLinus', 'friendshipsGeorge', 'friendshipsEmily', 'farmingLevel', 'statsRocksCrushed', 'statsDaysPlayed', 'statsStepsTaken', 'statsSpecificMonstersKilledFly', 'statsSpecificMonstersKilledGhost', 'statsSpecificMonstersKilledBat', 'statsSpecificMonstersKilledSkeleton', 'statsSpecificMonstersKilledGrub', 'statsSpecificMonstersKilledDust_Spirit', 'statsSpecificMonstersKilledStone_Golem', 'statsSpecificMonstersKilledFrost_Bat', 'statsSpecificMonstersKilledDuggy', 'statsSpecificMonstersKilledRock_Crab', 'statsSpecificMonstersKilledBig_Slime', 'statsSpecificMonstersKilledSludge', 'statsSpecificMonstersKilledFrost_Jelly', 'statsSpecificMonstersKilledBug', 'statsSpecificMonstersKilledGreen_Slime', 'statsSpecificMonstersKilledLava_Crab', 'statsSlimesKilled', 'statsPreservesMade', 'statsGeodesCracked', 'statsSeedsSown', 'statsNotesFound', 'statsMonstersKilled', 'statsStumpsChopped', 'statsCropsShipped', 'statsCowMilkProduced', 'statsFishCaught', 'statsPiecesOfTrashRecycled', 'statsTrufflesFound', 'statsIridiumFound', 'statsTimesFished', 'statsStarLevelCropsShipped', 'statsCopperFound', 'statsBarsSmelted', 'statsBouldersCracked', 'statsCoinsFound', 'statsCaveCarrotsFound', 'statsStoneGathered', 'statsQuestsCompleted', 'statsGoatMilkProduced', 'statsCoalFound', 'statsIronFound', 'statsCheeseMade', 'statsItemsCooked', 'statsWeedsEliminated', 'statsTimesUnconscious', 'statsChickenEggsLayed', 'statsSheepWoolProduced', 'statsDiamondsFound','statsRabbitWoolProduced', 'statsAverageBedtime', 'statsBeveragesMade', 'statsOtherPreciousGemsFound', 'statsDuckEggsLayed', 'statsItemsCrafted', 'statsGiftsGiven', 'statsSticksChopped', 'statsPrismaticShardsFound', 'statsDirtHoed', 'statsGoldFound', 'statsMysticStonesCrushed', 'statsItemsShipped', 'statsGoatCheeseMade', 'shirt', 'uniqueIDForThisGame', 'miningLevel', 'facialHair', 'money', 'newEyeColor0', 'newEyeColor1', 'newEyeColor2', 'newEyeColor3', 'maxStamina', 'farmName', 'foragingLevel', 'fishingLevel', 'deepestMineLevel', 'accessory', 'catPerson', 'totalMoneyEarned', 'millisecondsPlayed', 'hairstyleColor0', 'hairstyleColor1', 'hairstyleColor2', 'hairstyleColor3', 'name', 'professions0', 'professions1','professions2', 'professions3', 'professions4', 'professions5']
	crono = ['url', 'isMale', 'pantsColor0', 'pantsColor1', 'pantsColor2', 'pantsColor3', 'combatLevel', 'maxHealth', 'hair', 'favoriteThing', 'maxItems', 'skin', 'friendshipsWilly', 'friendshipsClint', 'friendshipsJodi', 'friendshipsHarvey', 'friendshipsLeah', 'friendshipsWizard', 'friendshipsJas', 'friendshipsAbigail', 'friendshipsMaru', 'friendshipsElliott', 'friendshipsCaroline', 'friendshipsPam', 'friendshipsShane', 'friendshipsDemetrius', 'friendshipsAlex', 'friendshipsGus', 'friendshipsVincent', 'friendshipsSebastian', 'friendshipsRobin', 'friendshipsSam', 'friendshipsLewis', 'friendshipsMarnie', 'friendshipsPenny', 'friendshipsHaley', 'friendshipsPierre', 'friendshipsEvelyn', 'friendshipsLinus', 'friendshipsGeorge', 'friendshipsEmily', 'farmingLevel', 'statsRocksCrushed', 'statsDaysPlayed', 'statsStepsTaken', 'statsSpecificMonstersKilledFly', 'statsSpecificMonstersKilledGhost', 'statsSpecificMonstersKilledBat', 'statsSpecificMonstersKilledGrub', 'statsSpecificMonstersKilledDust_Spirit', 'statsSpecificMonstersKilledStone_Golem','statsSpecificMonstersKilledFrost_Bat', 'statsSpecificMonstersKilledDuggy', 'statsSpecificMonstersKilledRock_Crab', 'statsSpecificMonstersKilledBig_Slime', 'statsSpecificMonstersKilledFrost_Jelly', 'statsSpecificMonstersKilledBug', 'statsSpecificMonstersKilledGreen_Slime', 'statsSlimesKilled', 'statsPreservesMade', 'statsGeodesCracked', 'statsSeedsSown', 'statsNotesFound', 'statsMonstersKilled', 'statsStumpsChopped', 'statsCropsShipped', 'statsCowMilkProduced', 'statsFishCaught', 'statsPiecesOfTrashRecycled', 'statsTrufflesFound', 'statsIridiumFound', 'statsTimesFished', 'statsStarLevelCropsShipped', 'statsCopperFound', 'statsBarsSmelted', 'statsBouldersCracked', 'statsCoinsFound', 'statsCaveCarrotsFound', 'statsStoneGathered', 'statsQuestsCompleted', 'statsGoatMilkProduced', 'statsCoalFound', 'statsIronFound', 'statsCheeseMade', 'statsItemsCooked', 'statsWeedsEliminated', 'statsTimesUnconscious', 'statsChickenEggsLayed', 'statsSheepWoolProduced', 'statsDiamondsFound', 'statsRabbitWoolProduced', 'statsAverageBedtime', 'statsBeveragesMade', 'statsOtherPreciousGemsFound', 'statsDuckEggsLayed', 'statsItemsCrafted', 'statsGiftsGiven', 'statsSticksChopped', 'statsPrismaticShardsFound','statsDirtHoed', 'statsGoldFound', 'statsMysticStonesCrushed', 'statsItemsShipped', 'statsGoatCheeseMade', 'shirt', 'uniqueIDForThisGame', 'miningLevel', 'facialHair', 'money', 'newEyeColor0', 'newEyeColor1', 'newEyeColor2', 'newEyeColor3', 'maxStamina', 'farmName', 'foragingLevel', 'fishingLevel', 'deepestMineLevel','accessory', 'catPerson', 'totalMoneyEarned', 'millisecondsPlayed', 'hairstyleColor0', 'hairstyleColor1', 'hairstyleColor2', 'hairstyleColor3', 'name', 'professions0', 'professions1', 'professions2', 'professions3', 'professions4']

	combined = list(set(sketchy+crono))
	for item in combined:
		if not (item in crono and item in sketchy):
			print item

