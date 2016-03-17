from generateAvatar import generateAvatar
from playerInfo import playerInfo
from PIL import Image
import json

def generateFamilyPortrait(player_img, partner, cat, children, scale=4):
	portrait = Image.new('RGBA', (48,48))
	if partner:
		partner_img = Image.open('./assets/partners/{0}.png'.format(partner))
	
	if cat:
		pet_img = Image.open('./assets/pets/cat.png')
	else:
		pet_img = Image.open('./assets/pets/dog.png')

	child_imgs = []
	for child in children:
		gender = ""
		if child[0] == 1 and child[2] > 42:
			gender = '_girl'
		skin = ""
		if child[1]:
			gender = '_dark'

		baby = False
		stage= "Toddler"
		if child[2] < 28:
			stage="Baby_cot"
			baby = True
		elif child[2] < 42: 
			stage="Baby_floor"
			baby = True

		child_imgs.append((Image.open('./assets/child/{0}{1}{2}.png'.format(stage, gender, skin)), baby))

	if partner: portrait.paste(partner_img, (14+8,0), partner_img)
	portrait.paste(player_img, (2+8,2), player_img)
	for i, (child_img, baby) in enumerate(child_imgs):
		if i == 0: 
			if baby:
				child_img = child_img.transpose(Image.FLIP_LEFT_RIGHT).resize((int(child_img.width/1.5), int(child_img.height/1.5)), Image.NEAREST)
				portrait.paste(child_img, (9,5), child_img)
			else:
				portrait.paste(child_img, (0,6), child_img)
		if i == 1: 
			if baby:
				child_img = child_img.resize((int(child_img.width/1.5), int(child_img.height/1.5)), Image.NEAREST)
				portrait.paste(child_img, (25,5), child_img)
			else:
				child_img = child_img.transpose(Image.FLIP_LEFT_RIGHT)
				portrait.paste(child_img, (27,6), child_img)

	portrait.paste(pet_img, (9+8,8), pet_img)
	
	portrait = portrait.resize((48*scale, 48*scale))
	return portrait.crop(portrait.getbbox())

def main():
	filelocation = './saves/Sketchy_116441313'
	player = playerInfo(filelocation)
	player_img = generateAvatar(player)
	portrait_info = json.loads(player['portrait_info'])
	generateFamilyPortrait(player_img, portrait_info['partner'], portrait_info['cat'], portrait_info['children']).save('test.png')

if __name__ == '__main__':
	main()