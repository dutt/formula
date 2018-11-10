from random import randint

import tcod

from messages import Message
import gfx
from map_objects.tile import Tile
from map_objects.rect import Rect
from entity import Entity, Pos
from components.fighter import Fighter
from components.ai import BasicMonster
from components.stairs import Stairs
from random_utils import random_choice_from_dict, from_dungeon_level


class GameMap:
    def __init__(self, size, dungeon_level=1):
        self.width = size.width
        self.height = size.height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities, timesystem):
        max_monsters_per_room = from_dungeon_level([[2,1],[3,4],[5,6]], self.dungeon_level)

        num_monsters = randint(max_monsters_per_room, max_monsters_per_room)
        monster_chances = { "orc" : 80,
                            "troll" : from_dungeon_level([[15, 3],[30, 5], [60, 7]], self.dungeon_level) }

        for i in range(num_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.pos.x == x and entity.pos.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == "orc":
                    fighter_component = Fighter(hp=20, defense=0, power=10, xp=0)
                    ai = BasicMonster()
                    monster = Entity(x, y, 'O', tcod.desaturated_green, "Orc", speed=100,
                                     blocks=True, render_order=gfx.RenderOrder.ACTOR,
                                     fighter=fighter_component, ai=ai)
                else:
                    fighter_component = Fighter(hp=30, defense=2, power=15, xp=0)
                    ai = BasicMonster()
                    monster = Entity(x, y, 'T', tcod.darker_green, "Troll", speed=100,
                                     blocks=True, render_order=gfx.RenderOrder.ACTOR,
                                     fighter=fighter_component, ai=ai)
                entities.append(monster)
                timesystem.register(monster)

    def make_map(self, constants, player, entities, timesystem):
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
                #no intersections
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y
                if len(rooms) == 0:
                    player.pos = Pos(new_x, new_y)
                else:
                    (prev_x, prev_y) = rooms[-1].center()

                    if randint(0,1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, new_x)
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                rooms.append(new_room)
                self.place_entities(new_room, entities, timesystem)

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', tcod.white, "Stairs",
                             render_order=gfx.RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    def next_floor(self, player, log, constants, entities, timesystem):
        # remove all on the current floor
        for e in entities:
            if e.pos != player.pos:
                timesystem.release(e)

        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants, player, entities, timesystem)
        player.fighter.heal(player.fighter.max_hp // 2)
        log.add_message(Message("You rest for a moment, and recover your strength", tcod.light_violet))
        return entities

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2)+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False