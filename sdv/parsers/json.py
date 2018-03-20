import random

from sdv.farmInfo import sprite, checkSurrounding, map_types

json_layout_map = {'regular': 0,
                   'fishing': 1,
                   'foraging': 2,
                   'mining': 3,
                   'combat': 4}


def parse_json(data):
    map_type = selectMapType(data)
    if map_type == 'unsupported_map':
        return {'type': map_type, 'data': {}}
    tiles = data['tiles'] + data['buildings']
    # ['name', 'x', 'y', 'w', 'h', 'index', 'type', 'growth', 'flipped', 'orientation']
    craftable_index = {
        'scarecrow': 8,
        'chest': 130,
        'furnace': 13,
        'charcoal': 114,
        'seed-maker': 25,
        'crystal': 21,
        'egg-press': 158,
        'lighting-rod': 9,
        'recycling-machine': 20,
        'slime-incubator': 156,
        'worm-bin': 154,
        'mayo': 24,
        'cheese-press': 16,
        'keg': 12,
        'loom': 17,
        'oil-maker': 19,
        'preserves': 15,
        'bee-hive': 10,
        'campfire': 146,
        'wood-lamp-post': 152,
        'iron-lamp-post': 153,
    }

    object_index = {
        'torch': 93,
        'sprinkler': 599,
        'q-sprinkler': 621,
        'irid-sprinkler': 645,
        'twig': 295,
        'stone': 450
    }

    crops = {
        'blue-jazz': 27,
        'cauliflower': 2,
        'garlic': 4,
        'green-bean': (1, 6),
        'kale': 5,
        'parsnip': 0,
        'potato': (3, 6),
        'rhubarb': (6, 6),
        'strawberry': (36, 6),
        'tulip': 26,
        'blueberry': (9, 6),
        'corn': (15, 6),
        'hops': (37, 6),
        'hot-pepper': (10, 6),
        'melon': (7, 6),
        'poppy': 28,
        'radish': 20,
        'red-cabbage': (13, 6),
        'starfruit': (14, 6),
        'summer-spangle': 29,
        'tomato': (8, 6),
        'wheat': 11,
        'amaranth': 39,
        'ancient-fruit': (24, 6),
        'artichoke': (17, 6),
        'beet': 22,
        'bok-choy': 19,
        'cranberry': (21, 6),
        'eggplant': (16, 6),
        'fairy-rose': 31,
        'grape': (38, 6),
        'pumpkin': (18, 6),
        'sunflower': 30,
        'yam': 12
    }

    plant_colours = {
        'poppy': [(252, 0, 0), (252, 168, 0), (251, 251, 253)],
        'tulip': [(226, 73, 10), (255, 162, 194), (255, 191, 255), (233, 195, 255), (255, 250, 10)],
        'fairy-rose': [(255, 127, 144), (199, 173, 248), (136, 116, 247), (166, 133, 248),
                       (182, 0, 249), (69, 220, 247)],
        'summer-spangle': [(226, 0, 211), (255, 144, 122), (255, 212, 0), (99, 255, 210),
                           (0, 2008, 255), (206, 91, 255)],
        'blue-jazz': [(94, 121, 255), (109, 131, 255), (35, 127, 255), (40, 150, 255),
                      (112, 207, 255), (191, 228, 255)]
    }

    random.seed(502)

    objects = []
    tree_types = ['apricot', 'cherry-tree', 'orange-tree', 'peach', 'apple', 'pomegranate', 'tree',
                  'maple-tree', 'oak-tree', 'pine-tree', 'mushroom']
    fence_types = ['fence', 'stone-fence', 'iron-fence', 'hardwood-fence']
    path_types = ['gravel-path', 'wood-path', 'steppingstone-path', 'crystal-path', 'road']
    floor_types = ['wood-floor', 'straw-floor', 'weathered-floor', 'stone-floor', 'crystal-floor']

    # Deal with different sized building footprints
    buildings2 = ['stable', 'gold-clock', 'junimo-hut', 'mill']
    buildings3 = ['silo', 'well', 'coop', 'water-obelisk', 'earth-obelisk', 'shed']
    buildings4 = ['barn']
    buildings7 = ['slime-hutch']

    for tile in tiles:
        obj = tile['type']
        x = int(int(tile['x']) / 16)
        y = int(int(tile['y']) / 16)

        if obj == 'grass':
            objects.append(
                    sprite('Grass', x, y, 1, 1, 20, 1, random.randint(2, 4), random.randint(0, 1),
                           None)
            )
        if obj == 'weeds':
            objects.append(
                    sprite('Object', x, y, 1, 1, 313 + random.randint(0, 2), 'Crafting', 0, None,
                           'Weeds')
            )
        elif obj == 'farmland':
            objects.append(
                    addhoedirt(x, y)
            )
            objects.append(
                    sprite('HoeDirtCrop', x, y, 1, 1, 0, 0, random.randint(4, 5),
                           random.randint(0, 1), None)
            )
        elif obj == 'trellis':
            objects.append(
                    addhoedirt(x, y)
            )
            objects.append(
                    sprite('HoeDirtCrop', x, y, 1, 1, 0, 1, random.randint(4, 6),
                           random.randint(0, 1), None)
            )
        elif obj == 'tulips':
            objects.append(
                    addhoedirt(x, y)
            )
            colour = (random.randint(200, 255), random.randint(0, 50), 0)
            days = random.randint(0, 8)
            objects.append(
                    sprite('HoeDirtCrop', x, y, 1, 1, 0, 26, random.randint(4, 5),
                           random.randint(0, 1), (colour, days))
            )
        elif obj in buildings2:
            objects.append(
                    sprite('Building', x, y, 4, 2, None, obj.replace('-', ' '), None, None, None)
            )
        elif obj in buildings3:
            objects.append(
                    sprite('Building', x, y, 4, 3, None, obj.replace('-', ' '), None, None, None)
            )
        elif obj in buildings4:
            objects.append(
                    sprite('Building', x, y, 4, 4, None, obj.replace('-', ' '), None, None, None)
            )
        elif obj in buildings7:
            objects.append(
                    sprite('Building', x, y - 1, 4, 7, None, obj.replace('-', ' '), None, None,
                           None)
            )
        elif obj in craftable_index:
            objects.append(
                    sprite('Object', x, y, 1, 1, craftable_index[obj], 'Crafting', 0, 0, 0)
            )
        elif obj == 'gate':
            objects.append(
                    sprite('Fence', x, y, 0, 0, 0, 0, True, 0, obj)
            )
        elif obj == 'large-rock':
            objects.append(
                    sprite('ResourceClump', x, y, 0, 0, None, 672, None, None, None)
            )
        elif obj == 'large-log':
            objects.append(
                    sprite('ResourceClump', x, y, 0, 0, None, 602, None, None, None)
            )
        elif obj == 'large-stump':
            objects.append(
                    sprite('ResourceClump', x, y, 0, 0, None, 600, None, None, None)
            )
        elif obj in crops:
            if type(crops[obj]) is tuple:
                t, s = crops[obj]
            else:
                t, s = crops[obj], 5

            o = None
            if t in [26, 27, 28, 29, 31]:
                o = (
                    plant_colours[obj][random.randint(0, len(plant_colours[obj]) - 1)],
                    5
                )

            objects.extend(
                    [
                        sprite('Crop', x, y, 1, 1, None, t, s, random.randint(0, 1), o),
                        addhoedirt(x, y)
                    ]
            )
        elif obj in object_index:
            if obj == 'torch':
                name = 'Torch'
            elif obj == 'sprinkler':
                name = 'Sprinkler'
            elif obj == 'q-sprinkler':
                name = 'Quality Sprinkler'
            elif obj == 'irid-sprinkler':
                name = 'Iridium Sprinkler'
            elif obj == 'twig' or obj == 'stone':
                name = obj.title()
            objects.append(
                    sprite('Object', x, y, 1, 1, object_index[obj], 'Crafting', 0, 0, name)
            )
        elif obj in fence_types:
            t = 1
            if 'stone' in obj:
                t = 2
            elif 'iron' in obj:
                t = 3
            elif 'hardwood' in obj:
                t = 5
            objects.append(
                    sprite('Fence', x, y, 1, 1, 0, t, False, 0, 0)
            )
        elif obj in tree_types:
            T = random.randint(1, 3)
            name = 'FruitTree'
            if 'apple' in obj:
                T = 5
            elif 'apricot' in obj:
                T = 1
            elif 'cherry' in obj:
                T = 0
            elif 'orange' in obj:
                T = 2
            elif 'peach' in obj:
                T = 3
            elif 'pomegranate' in obj:
                T = 4
            elif 'maple-tree' in obj:
                T = 2
            elif 'oak-tree' in obj:
                T = 1
            elif 'pine-tree' in obj:
                T = 3
            elif 'mushroom' in obj:
                T = 7

            if obj in ['tree', 'maple-tree', 'oak-tree', 'pine-tree', 'mushroom']:
                name = 'Tree'

            if obj != 'tree':
                x += 1
                y += 2

            objects.append(
                    sprite(name, x, y, 1, 1, 0, T, 5, random.randint(0, 1), 0)
            )
        elif obj in path_types:
            if 'gravel' in obj:
                T = 5
            elif 'wood' in obj:
                T = 6
            elif 'crystal' in obj:
                T = 7
            elif 'road' in obj:
                T = 8
            elif 'steppingstone' in obj:
                T = 9
            objects.append(
                    sprite('Flooring', x, y, 1, 1, None, T, 0, False, None)
            )
        elif obj in floor_types:
            if 'straw' in obj:
                T = 4
            elif 'wood' in obj:
                T = 0
            elif 'crystal' in obj:
                T = 3
            elif 'weathered' in obj:
                T = 2
            elif 'stone' in obj:
                T = 1
            objects.append(
                    sprite('Flooring', x, y, 1, 1, None, T, 0, False, None)
            )
        else:
            print('json input: obj not in known types: {} coords {}, {}'.format(obj, x, y))

    farm = {k.name: [a for a in objects if a.name == k.name] for k in objects}

    greenhouse = sprite('Greenhouse',
                        25, 12, 0, 6, 0,
                        None, None, None, None)
    try:
        g = False
        if data['options']['greenhouse']:
            g = True
    except:
        g = True

    if g:
        greenhouse = sprite('Greenhouse',
                            25, 12, 0, 6, 1,
                            None, None, None, None)

    house = sprite('House',
                   58, 14, 10, 6, 0,
                   None, None, None, None)

    farm['misc'] = [house, greenhouse]

    try:
        farm['HoeDirt'] = checkSurrounding(farm['HoeDirt'])
    except Exception as e:
        pass
    try:
        farm['Fence'] = checkSurrounding(farm['Fence'])
    except Exception as e:
        pass
    try:
        farm['Flooring'] = checkSurrounding(farm['Flooring'])
    except Exception as e:
        pass

    try:
        for i, fence in enumerate(farm['Fence']):
            if fence.growth and fence.orientation == 17:
                farm['Fence'][i] = fence._replace(y=fence.y - 1)
    except Exception as e:
        pass

    return_data = {'type': map_types[map_type], 'data': farm}
    return return_data


def selectMapType(data):
    try:
        json_options_layout = data['options']['layout']
    except:
        return 0
    if json_options_layout in json_layout_map:
        return json_layout_map[json_options_layout]
    else:
        return 'unsupported_map'


def addhoedirt(x, y):
    return sprite(
            name='HoeDirt',
            x=x,
            y=y,
            w=1, h=1,
            index=None,
            type=None,
            growth=None,
            flipped=None,
            orientation=None
    )