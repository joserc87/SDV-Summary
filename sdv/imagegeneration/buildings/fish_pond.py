from PIL import Image
from sdv.imagegeneration.tools import tintImage


def render_fish_pond(item, assets=None):
    if assets is None:
        raise ValueError("Assets must be defined")

    sprite_sheet = assets["buildings"]["fish pond"]

    result = Image.new("RGBA", (5 * 16, 7 * 16))

    water_tint = item.orientation.get("water_color")
    water = tintImage(sprite_sheet.crop((0, 5 * 16, 5 * 16, 10 * 16)), water_tint)
    result.paste(water, (0, 2 * 16), water)

    water_detail = sprite_sheet.crop((16, 10 * 16, 4 * 16, 11 * 16))
    result.paste(water_detail, (16, 3 * 16), water_detail)

    base = sprite_sheet.crop((0, 0, 5 * 16, 5 * 16))
    result.paste(base, (0, 2 * 16), base)

    if item.orientation.get("has_output"):
        output_bucket = sprite_sheet.crop((0, 10 * 16, 16, 11 * 16))
        result.paste(output_bucket, (4 * 16 + 1, 5 * 16 + 11), output_bucket)

    netting_style = item.orientation.get("netting_style")
    if netting_style is not None and netting_style in {0, 1, 2}:
        netting_height = 16 * 3
        netting_y = netting_style * netting_height
        netting = sprite_sheet.crop(
            (5 * 16, netting_y, 10 * 16, netting_y + netting_height)
        )
        result.paste(netting, (0, 0), netting)

    return result
