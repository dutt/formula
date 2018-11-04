import tcod

from messages import Message

from components.ai import ConfusedMonster


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get("amount")

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        msg = Message("You are already at full health", tcod.yellow)
        results.append({ "consumed" : False, "message" : msg})
    else:
        entity.fighter.heal(amount)
        msg = Message("You feel better", tcod.yellow)
        results.append({ "consumed" : True, "message" : msg})
    return results


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    damage = kwargs.get("damage")
    max_range = kwargs.get("max_range")
    results = []

    target = None
    closest_distance = max_range + 1

    for e in entities:
        if not e.fighter or e == caster or not tcod.map_is_in_fov(fov_map, e.x, e.y):
            continue
        distance = caster.distance_to(e)
        if distance < closest_distance:
            target = e
            closest_distance = distance

    if target:
        msg = Message("A lightning strikes the {} for {} damage".format(target.name, damage), tcod.red)
        results.append({"consumed" : True, "target" : target, "message" : msg})
        results.extend(target.fighter.take_damage(damage))
    else:
        msg = Message("No enemy within range".format(target.name, damage), tcod.red)
        results.append({ "consumed" : False, "message" : msg })

    return results


def cast_fireball(*args, **kwargs):
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    damage = kwargs.get("damage")
    radius = kwargs.get("radius")
    target_x = kwargs.get("target_x")
    target_y = kwargs.get("target_y")
    results = []

    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        msg = Message("You can't target a tile you don't see", tcod.yellow)
        return [{"consumed" : False, "message" : msg}]

    msg = Message("The fireball explodes, burning everything within {} tiles".format(radius, tcod.yellow))
    results.append({"consumed" : True, "message" : msg})

    for e in entities:
        if e.distance(target_x, target_y) <= radius and e.fighter:
            results.append({"message" : Message("The {} gets burned for {} hp".format(e.name, damage))})
            results.extend(e.fighter.take_damage(damage))
    return results


def cast_confuse(*args, **kwargs):
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    target_x = kwargs.get("target_x")
    target_y = kwargs.get("target_y")
    results = []

    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        msg = Message("You can't target a tile you don't see", tcod.yellow)
        return [{"consumed" : False, "message" : msg}]

    for e in entities:
        if e.x == target_x and e.y == target_y and e.ai:
            confused_ai = ConfusedMonster(e.ai, 10)
            confused_ai.owner = e
            e.ai = confused_ai

            results.append({ "consumed" : True,
                            "message" : Message("The {} looks confused".format(e.name), tcod.light_green)
                           })
            break
    else:
        results.append({"consumed" : False, "message" : Message("There is not targetable enemy there", tcod.yellow)})

    return results
