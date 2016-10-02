from PIL import Image
import os

def generateFamilyPortrait(player_img, information, scale=4):
    portrait = Image.new('RGBA', (48, 48))
    if information['partner']:
        partner_img = Image.open('./sdv/assets/npcs/partners/{0}.png'.format(information['partner']))

    if information['cat']:
        pet_img = Image.open('./sdv/assets/npcs/animals/cat.png')
    else:
        pet_img = Image.open('./sdv/assets/npcs/animals/dog.png')

    child_imgs = []
    for child in information['children']:
        gender = ""
        if child[0] == 1 and child[2] > 42:
            gender = '_girl'
        skin = ""
        if child[1]:
            gender = '_dark'

        baby = False
        stage = "Toddler"
        if child[2] < 28:
            stage = "Baby_cot"
            baby = True
        elif child[2] < 42:
            stage = "Baby_floor"
            baby = True

        child_imgs.append((Image.open('./sdv/assets/child/{0}{1}{2}.png'.format(stage, gender, skin)), baby))

    if information['partner']:
        portrait.paste(partner_img, (14+8, 0), partner_img)

    portrait.paste(player_img, (2+8, 2), player_img)
    for i, (child_img, baby) in enumerate(child_imgs):
        if i == 0:
            if baby:
                child_img = child_img.transpose(Image.FLIP_LEFT_RIGHT).resize((int(child_img.width/1.5), int(child_img.height/1.5)), Image.NEAREST)
                portrait.paste(child_img, (9, 4), child_img)
            else:
                portrait.paste(child_img, (0, 6), child_img)
        if i == 1:
            if baby:
                child_img = child_img.resize((int(child_img.width/1.5), int(child_img.height/1.5)), Image.NEAREST)
                portrait.paste(child_img, (25, 4), child_img)
            else:
                child_img = child_img.transpose(Image.FLIP_LEFT_RIGHT)
                portrait.paste(child_img, (27, 6), child_img)

    portrait.paste(pet_img, (9+8, 8), pet_img)
    portrait = portrait.resize((48*scale, 48*scale))
    return portrait.crop(portrait.getbbox())
