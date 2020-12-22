import os

from PIL import Image
from sdv import app
from sdv.imagegeneration.tools import cropImg

asset_dir = app.config.get("ASSET_PATH")

overlay_layers = {"Front", "AlwaysFront", "Buildings"}

SEASONS = {"spring", "summer", "fall", "winter"}

outdoor_tile_sheets = {
    season: Image.open(
        os.path.join(asset_dir, "farm", f"{season}_outdoorsTileSheet.png")
    )
    for season in SEASONS
}


def bin_lid():
    return Image.open(os.path.join(asset_dir, "farm", "looseSprites", "binLid.png"))


def shipping_bin():
    base = Image.open(os.path.join(asset_dir, "farm", "buildings", "Shipping Bin.png"))
    lid = bin_lid()
    base.paste(lid, (-1, 2), lid)
    return base


def get_spouse_area(spouse_name, season):
    sprite_sheet = outdoor_tile_sheets[season]
    spouse_area = Image.new("RGBA", (16 * 4, 16 * 4), (255, 255, 255, 0))

    if spouse_name == "sam":
        half_pipe_left = cropImg(sprite_sheet, 25 * 124 + 23, objectSize=(16, 32))
        half_pipe_right = cropImg(sprite_sheet, 25 * 124 + 24, objectSize=(16, 32))
        half_pipe_middle = cropImg(sprite_sheet, 25 * 126 + 23, objectSize=(32, 32))

        spouse_area.paste(half_pipe_left, (0, 16), half_pipe_left)
        spouse_area.paste(half_pipe_middle, (16, 16 * 2), half_pipe_middle)
        spouse_area.paste(half_pipe_right, (16 * 3, 16), half_pipe_right)
    elif spouse_name == "maru":
        gadget = cropImg(sprite_sheet, 25 * 123 + 24, objectSize=(16, 16))

        spouse_area.paste(gadget, (16 * 2, 16 * 2), gadget)
    elif spouse_name in {"abigail", "penny", "harvey", "elliott"}:
        plant_pot_empty = cropImg(sprite_sheet, 25 * 123 + 23, objectSize=(16, 16))
        plant_pot_full = cropImg(sprite_sheet, 25 * 122 + 23, objectSize=(16, 16))

        spouse_area.paste(plant_pot_full, (0, 16 * 2), plant_pot_full)
        spouse_area.paste(plant_pot_empty, (16 * 1, 16 * 2), plant_pot_empty)
        spouse_area.paste(plant_pot_full, (16 * 3, 16 * 2), plant_pot_full)
    elif spouse_name == "leah":
        sculpture = cropImg(sprite_sheet, 25 * 122 + 22, objectSize=(16, 32))

        spouse_area.paste(sculpture, (16, 16), sculpture)
    elif spouse_name == "sebastian":
        bike = cropImg(sprite_sheet, 25 * 155 + 2, objectSize=(16 * 3, 16 * 2))

        spouse_area.paste(bike, (16, 16), bike)
    elif spouse_name == "alex":
        kettle_bell = cropImg(sprite_sheet, 25 * 122 + 24, objectSize=(16, 16))
        spouse_area.paste(kettle_bell, (0, 16 * 2), kettle_bell)
    elif spouse_name == "emily":
        crystal_blue = cropImg(sprite_sheet, 25 * 153 + 16, objectSize=(16, 16))
        crystal_green = cropImg(sprite_sheet, 25 * 152 + 17, objectSize=(16, 16 * 2))
        crystal_pink = cropImg(sprite_sheet, 25 * 157 + 17, objectSize=(16, 16))

        spouse_area.paste(crystal_blue, (16 * 2, 16 * 2), crystal_blue)
        spouse_area.paste(crystal_blue, (0, 16 * 3), crystal_blue)
        spouse_area.paste(crystal_green, (0, 16 * 1), crystal_green)
        spouse_area.paste(crystal_green, (16 * 3, 16 * 1), crystal_green)
        spouse_area.paste(crystal_pink, (16, 16 * 2), crystal_pink)
        spouse_area.paste(crystal_pink, (16 * 3, 16 * 3), crystal_pink)
    elif spouse_name == "haley":
        palm = cropImg(sprite_sheet, 25 * 119 + 24, objectSize=(16, 16 * 3))

        spouse_area.paste(palm, (0, 0), palm)
        spouse_area.paste(palm, (16 * 3, 0), palm)
    elif spouse_name == "shane":
        roof = cropImg(sprite_sheet, 25 * 148 + 22, objectSize=(16 * 3, 16 * 2))
        body = cropImg(sprite_sheet, 25 * 155 + 15, objectSize=(16 * 3, 16 * 2))

        spouse_area.paste(roof, (16, 0), roof)
        spouse_area.paste(body, (16, 16 * 2), body)

    return spouse_area


def open_nicely(filename):
    im = Image.open(filename)
    im.load()
    return im


def load_overlays(season, base):
    overlays = dict()

    for layer in overlay_layers:
        overlays[layer] = list()
        overlay_path = os.path.join(asset_dir, "base", base, season, layer)
        farm_tile_height = 80 if base == "FourCorners" else 65
        for i in range(farm_tile_height):
            overlays[layer].append(
                open_nicely(os.path.join(overlay_path, "{}-{}.png".format(layer, i)))
            )
    return overlays


def loadFarmAssets(season="spring", base="Default"):
    assets = {
        "base": {
            base: {
                season: Image.open(
                    os.path.join(asset_dir, "base", base, season, "Back.png")
                )
            }
        },
        "overlays": {base: {season: load_overlays(season, base)}},
        "objects": Image.open(
            os.path.join(asset_dir, "farm", "tileSheets", "springobjects.png")
        ),
        "craftables": Image.open(
            os.path.join(asset_dir, "farm", "tileSheets", "Craftables.png")
        ),
        "flooring": Image.open(
            os.path.join(asset_dir, "farm", "terrainFeatures", "flooring.png")
        ),
        "hoe dirt": {
            "normal": Image.open(
                os.path.join(asset_dir, "farm", "terrainFeatures", "hoeDirt.png")
            ),
            "winter": Image.open(
                os.path.join(asset_dir, "farm", "terrainFeatures", "hoeDirtsnow.png")
            ),
        },
        "crops": Image.open(os.path.join(asset_dir, "farm", "tileSheets", "crops.png")),
        "fences": {
            "wood": Image.open(
                os.path.join(asset_dir, "farm", "looseSprites", "Fence1.png")
            ),
            "stone": Image.open(
                os.path.join(asset_dir, "farm", "looseSprites", "Fence2.png")
            ),
            "iron": Image.open(
                os.path.join(asset_dir, "farm", "looseSprites", "Fence3.png")
            ),
            "hardwood": Image.open(
                os.path.join(asset_dir, "farm", "looseSprites", "Fence5.png")
            ),
        },
        "bushes": Image.open(
            os.path.join(asset_dir, "farm", "terrainFeatures", "bushes.png")
        ),
        "trees": {
            "oak": {
                "spring": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree1_spring.png"
                    )
                ),
                "summer": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree1_summer.png"
                    )
                ),
                "fall": Image.open(
                    os.path.join(asset_dir, "farm", "terrainFeatures", "tree1_fall.png")
                ),
                "winter": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree1_winter.png"
                    )
                ),
            },
            "maple": {
                "spring": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree2_spring.png"
                    )
                ),
                "summer": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree2_summer.png"
                    )
                ),
                "fall": Image.open(
                    os.path.join(asset_dir, "farm", "terrainFeatures", "tree2_fall.png")
                ),
                "winter": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree2_winter.png"
                    )
                ),
            },
            "pine": {
                "spring": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree3_spring.png"
                    )
                ),
                "summer": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree3_spring.png"
                    )
                ),
                "fall": Image.open(
                    os.path.join(asset_dir, "farm", "terrainFeatures", "tree3_fall.png")
                ),
                "winter": Image.open(
                    os.path.join(
                        asset_dir, "farm", "terrainFeatures", "tree3_winter.png"
                    )
                ),
            },
            "mushroom": Image.open(
                os.path.join(asset_dir, "farm", "terrainFeatures", "mushroom_tree.png")
            ),
            "fruit": Image.open(
                os.path.join(asset_dir, "farm", "tileSheets", "fruitTrees.png")
            ),
        },
        "grass": Image.open(
            os.path.join(asset_dir, "farm", "terrainFeatures", "grass.png")
        ),
        "buildings": {
            "barn": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Barn.png")
            ),
            "big barn": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Big Barn.png")
            ),
            "deluxe barn": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Deluxe Barn.png")
            ),
            "coop": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Coop.png")
            ),
            "big coop": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Big Coop.png")
            ),
            "deluxe coop": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Deluxe Coop.png")
            ),
            "greenhouse": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "houses.png")
            ).crop((160, 0, 160 + 112, 144 * 3)),
            "house": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "houses.png")
            ).crop((0, 0, 160, 144 * 3)),
            "silo": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Silo.png")
            ),
            "slime hutch": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Slime Hutch.png")
            ),
            "stable": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Stable.png")
            ),
            "well": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Well.png")
            ),
            "earth obelisk": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Earth Obelisk.png")
            ),
            "gold clock": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Gold Clock.png")
            ),
            "junimo hut": {
                "spring": Image.open(
                    os.path.join(asset_dir, "farm", "buildings", "Junimo Hut.png")
                ).crop((0, 0, 48, 64)),
                "summer": Image.open(
                    os.path.join(asset_dir, "farm", "buildings", "Junimo Hut.png")
                ).crop((48, 0, 48 * 2, 64)),
                "fall": Image.open(
                    os.path.join(asset_dir, "farm", "buildings", "Junimo Hut.png")
                ).crop((48 * 2, 0, 48 * 3, 64)),
                "winter": Image.open(
                    os.path.join(asset_dir, "farm", "buildings", "Junimo Hut.png")
                ).crop((48 * 3, 0, 48 * 4, 64)),
            },
            "mill": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Mill.png")
            ),
            "shed": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Shed.png")
            ),
            "water obelisk": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Water Obelisk.png")
            ),
            "log cabin": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Log Cabin.png")
            ),
            "plank cabin": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Plank Cabin.png")
            ),
            "stone cabin": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Stone Cabin.png")
            ),
            "desert obelisk": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Desert Obelisk.png")
            ),
            "fish pond": Image.open(
                os.path.join(asset_dir, "farm", "buildings", "Fish Pond.png")
            ),
            "shipping bin": shipping_bin(),
        },
        "binLid": bin_lid(),
        "spouseArea": {
            "sam": {season: get_spouse_area("sam", season) for season in SEASONS},
            "maru": {season: get_spouse_area("maru", season) for season in SEASONS},
            "abigail": {
                season: get_spouse_area("abigail", season) for season in SEASONS
            },
            "leah": {season: get_spouse_area("leah", season) for season in SEASONS},
            "sebastian": {
                season: get_spouse_area("sebastian", season) for season in SEASONS
            },
            "alex": {season: get_spouse_area("alex", season) for season in SEASONS},
            "penny": {season: get_spouse_area("penny", season) for season in SEASONS},
            "harvey": {season: get_spouse_area("harvey", season) for season in SEASONS},
            "elliott": {
                season: get_spouse_area("elliott", season) for season in SEASONS
            },
            "emily": {season: get_spouse_area("emily", season) for season in SEASONS},
            "haley": {season: get_spouse_area("haley", season) for season in SEASONS},
            "shane": {season: get_spouse_area("shane", season) for season in SEASONS},
        },
    }
    return assets


def loadAvatarAssets():
    assets = {
        "base": {
            "male": Image.open(
                os.path.join(asset_dir, "player", "male", "male_base.png")
            ),
            "female": Image.open(
                os.path.join(asset_dir, "player", "female", "female_base.png")
            ),
        },
        "boots": {
            "male": Image.open(
                os.path.join(asset_dir, "player", "male", "male_boots.png")
            ),
            "female": Image.open(
                os.path.join(asset_dir, "player", "female", "female_boots.png")
            ),
        },
        "legs": {
            "male": Image.open(
                os.path.join(asset_dir, "player", "male", "male_legs.png")
            ),
            "female": Image.open(
                os.path.join(asset_dir, "player", "female", "female_legs.png")
            ),
        },
        "arms": {
            "male": Image.open(
                os.path.join(asset_dir, "player", "male", "male_arms.png")
            ),
            "female": Image.open(
                os.path.join(asset_dir, "player", "female", "female_arms.png")
            ),
        },
        "hair": Image.open(os.path.join(asset_dir, "player", "misc", "hairstyles.png")),
        "accessories": Image.open(
            os.path.join(asset_dir, "player", "misc", "accessories.png")
        ),
        "shirts": Image.open(os.path.join(asset_dir, "player", "misc", "shirts.png")),
        "skin colors": Image.open(
            os.path.join(asset_dir, "player", "misc", "skinColors.png")
        ),
    }

    return assets
