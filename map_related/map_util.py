import random

from components.ai import DummyMonsterAI, MeleeMonsterAI, RangedMonsterAI
from components.drawable import Drawable
from components.fighter import Fighter
from components.monster import Monster
from map_related.gamemap import GameMap
from util import Pos, Size


def load_map(path, level):
    with open(path, "r") as reader:
        content = reader.read()

    lines = content.split("\n")
    lines = [line for line in lines if line != ""]
    width = len(lines[0])
    height = len(lines)
    retr = GameMap(Size(width, height), level)
    for x in range(retr.width):
        for y in range(retr.height):
            if lines[y][x] == "P":
                retr.tiles[x][y].blocked = False
                retr.tiles[x][y].block_sight = False
                retr.player_pos = Pos(x, y)
                retr.orig_player_pos = Pos(x, y)
            elif lines[y][x] == " ":
                retr.tiles[x][y].blocked = False
                retr.tiles[x][y].block_sight = False
            elif lines[y][x] == "#":
                retr.tiles[x][y].blocked = True
                retr.tiles[x][y].block_sight = True
    retr.set_tile_info(retr.tiles)
    return retr


def print_map(m, room_ids=True, walls=True, extra_points=[]):
    for y in range(m.height):
        for x in range(m.width):
            if Pos(x, y) in extra_points:
                print("XX", end="")
            elif m.tiles[x][y].symbol:
                print(m.tiles[x][y].symbol, end="")
            elif m.tiles[x][y].blocked and walls:
                print("##", end="")
            elif m.tiles[x][y].hallway:
                print("--", end="")
            elif m.tiles[x][y].room != -1 and room_ids:
                print("{:2}".format(m.tiles[x][y].room), end="")
            else:
                print(" ", end="")
        print("")
    print("")


def get_monster(x, y, game_map, room, monster_choice, assets, entities):
    def create_pack(hp, defense, power, xp, asset, name):
        retr = []
        packsize = random.randint(1, 3)
        diffs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        clean_diffs = []
        for d in diffs:
            dpos = Pos(x + d[0], y + d[1])
            occupied = False
            if game_map.is_blocked(dpos.x, dpos.y):
                occupied = True
            else:
                for e in entities:
                    if (
                        e.pos == dpos
                        and dpos.x in range(room.x1 + 2, room.x2 - 2)
                        and dpos.y in range(room.y1 + 2, room.y2 - 2)
                    ):
                        occupied = True
            if not occupied:
                clean_diffs.append(d)
        if len(clean_diffs) < packsize and len(clean_diffs) < 3:
            packsize = len(clean_diffs)
        assert len(clean_diffs) >= packsize
        for w in range(packsize):
            diff_idx = random.randint(0, len(clean_diffs) - 1)
            diff = clean_diffs[diff_idx]
            wx, wy = x + diff[0], y + diff[1]
            clean_diffs.remove(diff)
            fighter_component = Fighter(hp=hp, defense=defense, power=power, xp=xp // packsize)
            ai = MeleeMonsterAI()
            drawable_component = Drawable(asset)
            # randname = "{}-{}".format(name, random.randint(0, 1000))
            monster = Monster(wx, wy, name, speed=150, fighter=fighter_component, ai=ai, drawable=drawable_component,)
            retr.append(monster)
        return retr

    monsters = []

    # tutorial
    if monster_choice == "idiot":
        fighter_component = Fighter(hp=10, defense=0, power=3, xp=0)
        ai = DummyMonsterAI()
        drawable_component = Drawable(assets.thug)
        monster = Monster(x, y, "Thug", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component,)
        monsters.append(monster)

    # easy
    elif monster_choice == "thug":
        fighter_component = Fighter(hp=20, defense=0, power=3, xp=40)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.thug)
        monster = Monster(x, y, "Thug", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component,)
        monsters.append(monster)
    elif monster_choice == "axe_thrower":
        fighter_component = Fighter(hp=10, defense=0, power=1, xp=40)
        ai = RangedMonsterAI()
        drawable_component = Drawable(assets.axe_thrower)
        monster = Monster(
            x, y, "Axe thrower", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component, range=5,
        )
        monsters.append(monster)
    elif monster_choice == "dog_group":
        monsters.extend(create_pack(hp=5, defense=0, power=1, xp=40, asset=assets.dog, name="Hound"))

    # medium
    elif monster_choice == "mercenary":
        fighter_component = Fighter(hp=50, defense=5, power=5, xp=100)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.mercenary)
        monster = Monster(x, y, "Mercenary", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component,)
        monsters.append(monster)
    elif monster_choice == "rifleman":
        fighter_component = Fighter(hp=30, defense=3, power=3, xp=100)
        ai = RangedMonsterAI()
        drawable_component = Drawable(assets.rifleman)
        monster = Monster(
            x, y, "Rifleman", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component, range=5,
        )
        monsters.append(monster)
    elif monster_choice == "boar_group":
        monsters.extend(create_pack(hp=15, defense=2, power=3, xp=60, asset=assets.boar, name="Boar"))

    # hard
    elif monster_choice == "stalker":
        fighter_component = Fighter(hp=50, defense=5, power=5, xp=200)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.stalker)
        monster = Monster(x, y, "Stalker", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component,)
        monsters.append(monster)
    elif monster_choice == "zapper":
        fighter_component = Fighter(hp=30, defense=3, power=3, xp=200)
        ai = RangedMonsterAI()
        drawable_component = Drawable(assets.zapper)
        monster = Monster(
            x, y, "Zapper", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component, range=5,
        )
        monsters.append(monster)
    elif monster_choice == "armored_bear_group":
        monsters.extend(create_pack(hp=30, defense=4, power=6, xp=200, asset=assets.armored_bear, name="Panzerbear",))

    # end of the world as we know it
    elif monster_choice == "boss":
        fighter_component = Fighter(hp=150, defense=15, power=8, xp=0)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.boss)
        monster = Monster(x, y, "Arina", speed=150, fighter=fighter_component, ai=ai, drawable=drawable_component,)
        monsters.append(monster)
    else:
        raise ValueError("Unknown choice: '{}'".format(monster_choice))
    assert monsters
    return monsters
