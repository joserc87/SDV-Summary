# creates db for SDV-Summary
import config

database_structure_dict = {'md5':'TEXT',
'url':'TEXT',
'isMale':'TEXT',
'pantsColor0':'BIGINT',
'pantsColor1':'BIGINT',
'pantsColor2':'BIGINT',
'pantsColor3':'BIGINT',
'combatLevel':'BIGINT',
'maxHealth':'BIGINT',
'hair':'BIGINT',
'favoriteThing':'TEXT',
'maxItems':'BIGINT',
'skin':'BIGINT',
'friendshipsWilly':'BIGINT',
'friendshipsClint':'BIGINT',
'friendshipsJodi':'BIGINT',
'friendshipsHarvey':'BIGINT',
'friendshipsLeah':'BIGINT',
'friendshipsWizard':'BIGINT',
'friendshipsJas':'BIGINT',
'friendshipsAbigail':'BIGINT',
'friendshipsMaru':'BIGINT',
'friendshipsElliott':'BIGINT',
'friendshipsCaroline':'BIGINT',
'friendshipsPam':'BIGINT',
'friendshipsDwarf':'BIGINT',
'friendshipsShane':'BIGINT',
'friendshipsDemetrius':'BIGINT',
'friendshipsAlex':'BIGINT',
'friendshipsGus':'BIGINT',
'friendshipsVincent':'BIGINT',
'friendshipsSebastian':'BIGINT',
'friendshipsRobin':'BIGINT',
'friendshipsSam':'BIGINT',
'friendshipsLewis':'BIGINT',
'friendshipsMarnie':'BIGINT',
'friendshipsPenny':'BIGINT',
'friendshipsHaley':'BIGINT',
'friendshipsPierre':'BIGINT',
'friendshipsEvelyn':'BIGINT',
'friendshipsLinus':'BIGINT',
'friendshipsGeorge':'BIGINT',
'friendshipsEmily':'BIGINT',
'farmingLevel':'BIGINT',
'statsRocksCrushed':'BIGINT',
'statsDaysPlayed':'BIGINT',
'statsStepsTaken':'BIGINT',
'statsSpecificMonstersKilledFly':'BIGINT',
'statsSpecificMonstersKilledGhost':'BIGINT',
'statsSpecificMonstersKilledBat':'BIGINT',
'statsSpecificMonstersKilledSkeleton':'BIGINT',
'statsSpecificMonstersKilledGrub':'BIGINT',
'statsSpecificMonstersKilledDust_Spirit':'BIGINT',
'statsSpecificMonstersKilledStone_Golem':'BIGINT',
'statsSpecificMonstersKilledFrost_Bat':'BIGINT',
'statsSpecificMonstersKilledDuggy':'BIGINT',
'statsSpecificMonstersKilledRock_Crab':'BIGINT',
'statsSpecificMonstersKilledBig_Slime':'BIGINT',
'statsSpecificMonstersKilledSludge':'BIGINT',
'statsSpecificMonstersKilledFrost_Jelly':'BIGINT',
'statsSpecificMonstersKilledBug':'BIGINT',
'statsSpecificMonstersKilledGreen_Slime':'BIGINT',
'statsSpecificMonstersKilledLava_Crab':'BIGINT',
'statsSpecificMonstersKilledLava_Bat':'BIGINT',
'statsSpecificMonstersKilledMetal_Head':'BIGINT',
'statsSpecificMonstersKilledShadow_Brute':'BIGINT',
'statsSpecificMonstersKilledShadow_Shaman':'BIGINT',
'statsSlimesKilled':'BIGINT',
'statsPreservesMade':'BIGINT',
'statsGeodesCracked':'BIGINT',
'statsSeedsSown':'BIGINT',
'statsNotesFound':'BIGINT',
'statsMonstersKilled':'BIGINT',
'statsStumpsChopped':'BIGINT',
'statsCropsShipped':'BIGINT',
'statsCowMilkProduced':'BIGINT',
'statsFishCaught':'BIGINT',
'statsPiecesOfTrashRecycled':'BIGINT',
'statsTrufflesFound':'BIGINT',
'statsIridiumFound':'BIGINT',
'statsTimesFished':'BIGINT',
'statsStarLevelCropsShipped':'BIGINT',
'statsCopperFound':'BIGINT',
'statsBarsSmelted':'BIGINT',
'statsBouldersCracked':'BIGINT',
'statsCoinsFound':'BIGINT',
'statsCaveCarrotsFound':'BIGINT',
'statsStoneGathered':'BIGINT',
'statsQuestsCompleted':'BIGINT',
'statsGoatMilkProduced':'BIGINT',
'statsCoalFound':'BIGINT',
'statsIronFound':'BIGINT',
'statsCheeseMade':'BIGINT',
'statsItemsCooked':'BIGINT',
'statsWeedsEliminated':'BIGINT',
'statsTimesUnconscious':'BIGINT',
'statsChickenEggsLayed':'BIGINT',
'statsSheepWoolProduced':'BIGINT',
'statsDiamondsFound':'BIGINT',
'statsRabbitWoolProduced':'BIGINT',
'statsAverageBedtime':'BIGINT',
'statsBeveragesMade':'BIGINT',
'statsOtherPreciousGemsFound':'BIGINT',
'statsDuckEggsLayed':'BIGINT',
'statsItemsCrafted':'BIGINT',
'statsGiftsGiven':'BIGINT',
'statsSticksChopped':'BIGINT',
'statsPrismaticShardsFound':'BIGINT',
'statsDirtHoed':'BIGINT',
'statsGoldFound':'BIGINT',
'statsMysticStonesCrushed':'BIGINT',
'statsItemsShipped':'BIGINT',
'statsGoatCheeseMade':'BIGINT',
'shirt':'BIGINT',
'uniqueIDForThisGame':'BIGINT',
'miningLevel':'BIGINT',
'facialHair':'BIGINT',
'money':'BIGINT',
'newEyeColor0':'BIGINT',
'newEyeColor1':'BIGINT',
'newEyeColor2':'BIGINT',
'newEyeColor3':'BIGINT',
'maxStamina':'BIGINT',
'farmName':'TEXT',
'foragingLevel':'BIGINT',
'fishingLevel':'BIGINT',
'deepestMineLevel':'BIGINT',
'accessory':'BIGINT',
'catPerson':'TEXT',
'totalMoneyEarned':'BIGINT',
'millisecondsPlayed':'BIGINT',
'hairstyleColor0':'BIGINT',
'hairstyleColor1':'BIGINT',
'hairstyleColor2':'BIGINT',
'hairstyleColor3':'BIGINT',
'name':'TEXT',
'professions0':'TEXT',
'professions1':'TEXT',
'professions2':'TEXT',
'professions3':'TEXT',
'professions4':'TEXT',
'professions5':'TEXT',
'professions6':'TEXT',
'professions7':'TEXT',
'professions8':'TEXT',
'professions9':'TEXT',
'farm_info':'TEXT',
'farm_url':'TEXT',
'avatar_url':'TEXT',
'added_time':'FLOAT',
'ip':'TEXT',
'del_token':'BIGINT',
'views':'BIGINT',
'date':'TEXT',
'savefileLocation':'TEXT',
'petName':'TEXT'}

if config.USE_SQLITE==True:
	database_structure_dict['id']='INTEGER PRIMARY KEY AUTOINCREMENT'
else:
	database_structure_dict['id']='SERIAL PRIMARY KEY'

database_fields = ''
for key in sorted(database_structure_dict.keys()):
	database_fields+=key+','
database_fields = database_fields[:-1]

def generate_db():
	database_structure = ''
	for key in sorted(database_structure_dict.keys()):
		database_structure += key + ' ' +database_structure_dict[key] + ',\n'
	database_structure = database_structure[:-2]

	errors_structure = 'id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, time BIGINT, notes TEXT'
	todo_structure = 'id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, playerid TEXT'

	if config.USE_SQLITE == True:
		import sqlite3
		connection = sqlite3.connect(config.DB_SQLITE)
	else:
		import psycopg2
		connection = psycopg2.connect('dbname='+config.DB_NAME+' user='+config.DB_USER+' password='+config.DB_PASSWORD)
		errors_structure = errors_structure.replace(' INTEGER PRIMARY KEY AUTOINCREMENT',' SERIAL PRIMARY KEY')
		todo_structure = todo_structure.replace(' INTEGER PRIMARY KEY AUTOINCREMENT',' SERIAL PRIMARY KEY')


	c = connection.cursor()
	c.execute('CREATE TABLE playerinfo('+database_structure+')')
	c.execute('CREATE TABLE errors('+errors_structure+')')
	c.execute('CREATE TABLE todo('+todo_structure+')')
	connection.commit()

def delete_db():
	if config.USE_SQLITE == True:
		import sqlite3
		connection = sqlite3.connect(config.DB_SQLITE)
	else:
		import psycopg2
		connection = psycopg2.connect('dbname='+config.DB_NAME+' user='+config.DB_USER+' password='+config.DB_PASSWORD)

	c = connection.cursor()
	c.execute('DROP TABLE playerinfo')
	c.execute('DROP TABLE errors')
	c.execute('DROP TABLE todo')
	connection.commit()
	connection.close()

if __name__ == "__main__":
	generate_db()

