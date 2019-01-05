import random

from components.ai import MeleeMonsterAI, RangedMonsterAI
from components.drawable import Drawable
from components.fighter import Fighter
from components.monster import Monster
from map_related.gamemap import GameMap
from util import Pos


def load_map(path):
    with open(path, 'r') as reader:
        content = reader.read()

    lines = content.split("\n")
    lines = [line for line in lines if line != ""]
    width = len(lines[0])
    height = len(lines)
    retr = GameMap(width, height)
    for x in range(retr.width):
        for y in range(retr.height):
            if lines[y][x] == 'P':
                retr.tiles[x][y].blocked = False
                retr.tiles[x][y].block_sight = False
                retr.player_pos = Pos(x, y)
            elif lines[y][x] == ' ':
                retr.tiles[x][y].blocked = False
                retr.tiles[x][y].block_sight = False
    retr.set_tile_info(retr.tiles)


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


def get_monster(x, y, room, monster_choice, assets, entities):
    monsters = []
    if monster_choice == "ghost":
        fighter_component = Fighter(hp=20, defense=0, power=3, xp=35)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.ghost)
        monster = Monster(x, y, "Ghost", speed=100,
                          fighter=fighter_component, ai=ai, drawable=drawable_component)
        monsters.append(monster)
    elif monster_choice == "chucker":
        fighter_component = Fighter(hp=10, defense=0, power=1, xp=35)
        ai = RangedMonsterAI()
        drawable_component = Drawable(assets.chucker)
        monster = Monster(x, y, "Chucker", speed=100,
                          fighter=fighter_component, ai=ai, drawable=drawable_component,
                          range=5)
        monsters.append(monster)
    elif monster_choice == "wolfpack":
        packsize = random.randint(1, 3)
        diffs = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1), (0, 1),
                 (1, -1), (1, 0), (1, 1)]
        clean_diffs = []
        for d in diffs:
            dpos = Pos(x + d[0], y + d[1])
            occupied = False
            for e in entities:
                if e.pos == dpos and dpos.x in range(room.x1 + 2, room.x2 - 2) and dpos.y in range(room.y1 + 2,
                                                                                                   room.y2 - 2):
                    occupied = True
            if not occupied:
                clean_diffs.append(d)
        for w in range(packsize):
            diff_idx = random.randint(0, len(clean_diffs) - 1)
            diff = clean_diffs[diff_idx]
            wx, wy = x + diff[0], y + diff[1]
            clean_diffs.remove(diff)
            fighter_component = Fighter(hp=5, defense=0, power=1, xp=35)
            ai = MeleeMonsterAI()
            drawable_component = Drawable(assets.wolf)
            monster = Monster(wx, wy, "Wolf", speed=150,
                              fighter=fighter_component, ai=ai, drawable=drawable_component)
            monsters.append(monster)
    elif monster_choice == "demon":
        fighter_component = Fighter(hp=50, defense=5, power=5, xp=100)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.demon)
        monster = Monster(x, y, "Demon", speed=100,
                          fighter=fighter_component, ai=ai, drawable=drawable_component)
        monsters.append(monster)
    else:
        raise ValueError("Unknown choice: '{}'".format(monster_choice))
    assert monsters
    return monsters
