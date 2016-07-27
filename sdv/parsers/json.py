import random

from sdv.farmInfo import sprite, checkSurrounding


def parse_json(data):

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
        'campfire': 146
    }

    object_index = {
        'torch': 93,
        'sprinkler': 599,
        'q-sprinkler': 621,
        'irid-sprinkler': 645
    }

    random.seed(502)
    objects = []
    tree_types = ['apricot', 'cherry-tree', 'orange-tree', 'peach', 'apple', 'pomegranate', 'tree']
    fence_types = ['fence', 'stone-fence', 'iron-fence', 'hardwood-fence']
    path_types = ['gravel-path', 'wood-path', 'steppingstone-path', 'crystal-path', 'road']
    floor_types = ['wood-floor', 'straw-floor', 'weathered-floor', 'stone-floor', 'crystal-floor']

    for tile in tiles:
        type = tile['type']
        x = int(int(tile['x']) / 16)
        y = int(int(tile['y']) / 16)

        if type == 'grass':
            objects.append(
                sprite('Grass', x, y, 1, 1, 20, 1, random.randint(2, 4), random.randint(0, 1), None)
            )
        elif type == 'farmland':
            objects.append(
                addhoedirt(x, y)
            )
            objects.append(
                sprite('HoeDirtCrop', x, y, 1, 1, 0, 0, random.randint(4, 5), random.randint(0, 1), None)
            )
        elif type == 'trellis':
            objects.append(
                addhoedirt(x, y)
            )
            objects.append(
                sprite('HoeDirtCrop', x, y, 1, 1, 0, 1, random.randint(4, 6), random.randint(0, 1), None)
            )
        elif type == 'tulips':
            objects.append(
                addhoedirt(x, y)
            )
            colour = (random.randint(200, 255), random.randint(0, 50), 0)
            days = random.randint(0, 8)
            objects.append(
                sprite('HoeDirtCrop', x, y, 1, 1, 0, 26, random.randint(4, 5), random.randint(0, 1), (colour, days))
            )
        elif type == 'silo':
            objects.append(
                sprite('Building', x, y, 3, 3, None, 'silo', None, None, None)
            )
        elif type == 'well':
            objects.append(
                sprite('Building', x, y, 3, 3, None, 'well', None, None, None)
            )
        elif type == 'coop':
            objects.append(
                sprite('Building', x, y, 6, 3, None, 'coop', None, None, None)
            )
        elif type == 'barn':
            objects.append(
                sprite('Building', x, y, 7, 4, None, 'barn', None, None, None)
            )
        elif type == 'stable':
            objects.append(
                sprite('Building', x, y, 4, 2, None, 'stable', None, None, None)
            )
        elif type == 'slime-hutch':
            objects.append(
                sprite('Building', x, y, 11, 5, None, 'slime hutch', None, None, None)
            )
        elif type in craftable_index:
            objects.append(
                sprite('Object', x, y-1, 1, 1, craftable_index[type], 'Crafting', 0, 0, 0)
            )
        elif type == 'gate':
            objects.append(
                sprite('Fence', x, y, 0, 0, 0, 0, True, 0, type)
            )
        elif type in object_index:
            if type == 'torch':
                name = 'Torch'
            elif type == 'sprinkler':
                name = 'Sprinkler'
            elif type == 'q-sprinkler':
                name = 'Quality Sprinkler'
            elif type == 'irid-sprinkler':
                name = 'Iridium Sprinkler'
            objects.append(
                sprite('Object', x, y - 1, 1, 1, object_index[type], 'Crafting', 0, 0, name)
            )
        elif type in fence_types:
            t = 1
            if 'stone' in type:
                t = 2
            elif 'iron' in type:
                t = 3
            elif 'hardwood' in type:
                t = 5
            objects.append(
                sprite('Fence', x, y, 1, 1, 0, t, False, 0, 0)
            )
        elif type in tree_types:
            T = random.randint(1, 3)
            name = 'FruitTree'
            if 'apple' in type:
                T = 5
            elif 'apricot' in type:
                T = 1
            elif 'cherry' in type:
                T = 0
            elif 'orange' in type:
                T = 2
            elif 'peach' in type:
                T= 3
            elif 'pomegranate' in type:
                T = 4

            if type == 'tree':
                name = 'Tree'

            if type != 'tree':
                x += 1
                y += 2

            objects.append(
                sprite(name, x, y, 1, 1, 0, T, 5, random.randint(0, 1), 0)
            )
        elif type in path_types:
            if 'gravel' in type:
                T = 5
            elif 'wood' in type:
                T = 6
            elif 'crystal' in type:
                T = 7
            elif 'road' in type:
                T = 8
            elif 'steppingstone' in type:
                T = 9
            objects.append(
                sprite('Flooring', x, y, 1, 1, None, T, 0, False, None)
            )
        elif type in floor_types:
            if 'straw' in type:
                T = 4
            elif 'wood' in type:
                T = 0
            elif 'crystal' in type:
                T = 3
            elif 'weathered' in type:
                T = 2
            elif 'stone' in type:
                T = 1
            objects.append(
                sprite('Flooring', x, y, 1, 1, None, T, 0, False, None)
            )

    farm = {k.name: [a for a in objects if a.name == k.name] for k in objects}

    greenhouse = sprite('Greenhouse',
                        25, 12, 0, 6, 0,
                        None, None, None, None)

    if data['options']['greenhouse']:
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

    for i, fence in enumerate(farm['Fence']):
        if fence.growth and fence.orientation == 17:
            farm['Fence'][i] = fence._replace(y = fence.y - 1)

    return farm


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
