import random

from components.ai import DummyMonsterAI, MeleeMonsterAI, RangedMonsterAI
from components.drawable import Drawable
from components.fighter import Fighter
from components.monster import Monster
from util import Pos, Size
from graphics.assets import Assets
from components.damage_type import DamageType

def get_monster(x, y, game_map, room, monster_choice, entities):
    assets = Assets.get()

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
            monster = Monster(wx, wy, name, speed=150, fighter=fighter_component, ai=ai, drawable=drawable_component)
            retr.append(monster)
        return retr

    monsters = []

    # tutorial
    if monster_choice == "idiot":
        fighter_component = Fighter(hp=1, defense=0, power=0, xp=0)
        ai = DummyMonsterAI()
        drawable_component = Drawable(assets.thug)
        monster = Monster(x, y, "Thug", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component)
        monsters.append(monster)

    # easy
    elif monster_choice == "thug":
        fighter_component = Fighter(hp=15, defense=0, power=3, xp=40)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.thug)
        monster = Monster(x, y, "Thug", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component)
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
        fighter_component = Fighter(hp=25, defense=5, power=5, xp=100)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.mercenary)
        monster = Monster(x, y, "Mercenary", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component)
        monsters.append(monster)
    elif monster_choice == "rifleman":
        fighter_component = Fighter(hp=15, defense=3, power=3, xp=100)
        ai = RangedMonsterAI()
        drawable_component = Drawable(assets.rifleman)
        monster = Monster(
            x, y, "Rifleman", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component, range=5,
        )
        monsters.append(monster)
    elif monster_choice == "boar_group":
        monsters.extend(create_pack(hp=10, defense=2, power=3, xp=60, asset=assets.boar, name="Boar"))

    # hard
    elif monster_choice == "stalker":
        fighter_component = Fighter(hp=35, defense=5, power=7, xp=200)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.stalker)
        monster = Monster(x, y, "Stalker", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component)
        monsters.append(monster)
    elif monster_choice == "zapper":
        fighter_component = Fighter(hp=20, defense=3, power=3, xp=200)
        ai = RangedMonsterAI()
        drawable_component = Drawable(assets.zapper)
        monster = Monster(
            x, y, "Zapper", speed=100, fighter=fighter_component, ai=ai, drawable=drawable_component, range=5,
        )
        monsters.append(monster)
    elif monster_choice == "armored_bear_group":
        monsters.extend(create_pack(hp=15, defense=4, power=5, xp=200, asset=assets.armored_bear, name="Panzerbear"))

    # end of the world as we know it
    elif monster_choice == "boss":
        fighter_component = Fighter(hp=150, defense=15, power=8, xp=0)
        ai = MeleeMonsterAI()
        drawable_component = Drawable(assets.boss)
        monster = Monster(x, y, "Arina", speed=150, fighter=fighter_component, ai=ai, drawable=drawable_component)
        monsters.append(monster)
    else:
        raise ValueError("Unknown choice: '{}'".format(monster_choice))
    assert monsters
    return monsters
