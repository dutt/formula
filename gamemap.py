from random import randint

import tcod

from components.ai import MeleeMonsterAI, RangedMonsterAI
from components.drawable import Drawable
from components.fighter import Fighter
from components.monster import Monster
from components.stairs import Stairs
from entity import Entity
from graphics.render_order import RenderOrder
from map_objects.rect import Rect
from map_objects.tile import Tile
from messages import Message
from random_utils import random_choice_from_dict, from_dungeon_level
from util import Pos

class GameMap:
    def __init__(self, size, assets, dungeon_level, constants, monster_chances):
        self.width = size.width
        self.height = size.height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level
        self.assets = assets
        self.entities = []
        self.monster_chances = monster_chances
        self.make_map(constants)

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def get_monster(self, x, y, room, monster_choice):
        monsters = []
        if monster_choice == "ghost":
            fighter_component = Fighter(hp=20, defense=0, power=3, xp=35)
            ai = MeleeMonsterAI()
            drawable_component = Drawable(self.assets.ghost)
            monster = Monster(x, y, "Ghost", speed=100,
                              fighter=fighter_component, ai=ai, drawable=drawable_component)
            monsters.append(monster)
        elif monster_choice == "chucker":
            fighter_component = Fighter(hp=10, defense=0, power=1, xp=35)
            ai = RangedMonsterAI()
            drawable_component = Drawable(self.assets.chucker)
            monster = Monster(x, y, "Chucker", speed=100,
                              fighter=fighter_component, ai=ai, drawable=drawable_component,
                              range=5)
            monsters.append(monster)
        elif monster_choice == "wolfpack":
            packsize = randint(1, 3)
            diffs = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1 ),
                     (1, -1),  (1, 0),  (1, 1 )]
            clean_diffs = []
            for d in diffs:
                occupied = False
                for e in self.entities:
                    if e.pos == Pos(x + d[0], y + d[1]):
                        occupied = True
                if not occupied:
                    clean_diffs.append(d)
            for w in range(packsize):
                diff_idx = randint(0, len(clean_diffs)-1)
                diff = clean_diffs[diff_idx]
                wx, wy = x + diff[0], y + diff[1]
                clean_diffs.remove(diff)
                fighter_component = Fighter(hp=5, defense=0, power=1, xp=35)
                ai = MeleeMonsterAI()
                drawable_component = Drawable(self.assets.wolf)
                monster = Monster(wx, wy, "Wolf", speed=150,
                                  fighter=fighter_component, ai=ai, drawable=drawable_component)
                monsters.append(monster)
        elif monster_choice == "demon":
            fighter_component = Fighter(hp=50, defense=5, power=5, xp=100)
            ai = MeleeMonsterAI()
            drawable_component = Drawable(self.assets.demon)
            monster = Monster(x, y, "Demon", speed=100,
                              fighter=fighter_component, ai=ai, drawable=drawable_component)
            monsters.append(monster)
        else:
            raise ValueError("Unknown choice: '{}'".format(monster_choice))
        assert monster
        return monsters

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level + 1)

        num_monsters = randint(0, max_monsters_per_room)

        for i in range(num_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.pos.x == x and entity.pos.y == y]):
                monster_choice = random_choice_from_dict(self.monster_chances)
                entities.extend(self.get_monster(x, y, room, monster_choice))

    def make_map(self, constants):
        rooms = []
        center_of_last_room_x = None
        center_of_last_room_y = None
        for i in range(constants.max_rooms):
            w = randint(constants.room_min_size, constants.room_max_size)
            h = randint(constants.room_min_size, constants.room_max_size)
            x = randint(0, constants.map_size.width - w - 1)
            y = randint(0, constants.map_size.height - h - 1)

            new_room = Rect(x, y, w, h)
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # no intersections
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y
                if len(rooms) == 0:
                    self.player_pos = Pos(new_x, new_y)
                else:
                    (prev_x, prev_y) = rooms[-1].center()

                    if randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, new_x)
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                rooms.append(new_room)
                self.place_entities(new_room, self.entities)

        stairs_component = Stairs(self.dungeon_level + 1)
        drawable_component = Drawable(self.assets.stairs)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, "Stairs",
                             render_order=RenderOrder.STAIRS, stairs=stairs_component, drawable=drawable_component)
        self.entities.append(down_stairs)

    def next_floor(self, player, log, constants, entities, timesystem):
        # remove all on the current floor
        for e in entities:
            if e.pos != player.pos and e.active:
                timesystem.release(e)

        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants, player, entities, timesystem)
        player.fighter.heal(player.fighter.max_hp // 2)
        log.add_message(Message("You rest for a moment, and recover your strength", tcod.light_violet))
        return entities

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False
