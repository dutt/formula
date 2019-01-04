import random
from enum import Enum, auto

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
from util import Pos, Rect


class Dir(Enum):
    horizontal = auto()
    vertical = auto()


def mark_room(m, chunk, room):
    for x in range(chunk.x, chunk.x + chunk.width):
        for y in range(chunk.y, chunk.y + chunk.height):
            m.tiles[x][y].hallway = False
            m.tiles[x][y].room = room
        m.tiles[x][chunk.y].blocked = True
        m.tiles[x][chunk.y].block_sight = True
        m.tiles[x][chunk.y + chunk.height - 1].blocked = True
        m.tiles[x][chunk.y + chunk.height - 1].block_sight = True
    for y in range(chunk.y, chunk.y + chunk.height):
        m.tiles[chunk.x][y].blocked = True
        m.tiles[chunk.x][y].block_sight = True
        m.tiles[chunk.x + chunk.width - 1][y].blocked = True
        m.tiles[chunk.x + chunk.width - 1][y].block_sight = True
    chunk.room = room


def mark_hallway(m, chunk, pos, direction):
    if direction == Dir.vertical:
        for y in range(chunk.y, chunk.y + chunk.height):
            m.tiles[pos][y].hallway = True
            m.tiles[pos][y].room = -1
    else:
        for x in range(chunk.x, chunk.x + chunk.width):
            m.tiles[x][pos].hallway = True
            m.tiles[x][pos].room = -1


def pop_largest(chunks):
    size = 0
    retr_idx = None
    for idx, c in enumerate(chunks):
        if c.width * c.height > size:
            size = c.width * c.height
            retr_idx = idx
    retr = chunks.pop(retr_idx)
    return retr


# first pass. split floor into chunks and hallways
def chunkify(m):
    direction = Dir.horizontal
    start_chunk = Rect(0, 0, m.width, m.height)
    mark_room(m, start_chunk, 0)
    chunks = [start_chunk]
    minsize = 13
    minlength = 6
    while m.free_area < m.total_size * 0.2:
        curr = pop_largest(chunks)
        if direction == Dir.vertical and curr.width > minsize:
            start = curr.x + max(minlength, int(curr.width * 0.2))
            end = curr.x + curr.width - max(minlength, int(curr.width * 0.2))
            hallway = random.randint(start, end)
            first = Rect(curr.x, curr.y, hallway - curr.x, curr.height)
            second = Rect(hallway + 1, curr.y, curr.x + curr.width - hallway - 1, curr.height)
            new_direction = Dir.horizontal
        elif direction == Dir.horizontal and curr.height > minsize:  # horizontal
            start = curr.y + max(minlength, int(curr.height * 0.2))
            end = curr.y + curr.height - max(minlength, int(curr.height * 0.2))
            hallway = random.randint(start, end)
            first = Rect(curr.x, curr.y, curr.width, hallway - curr.y)
            second = Rect(curr.x, hallway + 1, curr.width, curr.y + curr.height - hallway - 1)
            new_direction = Dir.vertical
        else:  # chunk too small, done. just re-add the chunk
            chunks.append(curr)
            break

        mark_room(m, first, m.first_unused_room_id)
        chunks.append(first)

        mark_room(m, second, m.first_unused_room_id)
        chunks.append(second)

        mark_hallway(m, curr, hallway, direction)
        direction = new_direction

        # print_map(m)

    return chunks


def cleanup_walls(m):
    t = m.tiles

    # first remove walls between corridors
    for x in range(2, m.width - 2):
        for y in range(2, m.height - 2):
            if t[x][y - 1].hallway and t[x][y].blocked and t[x][y + 1].hallway:
                t[x][y].hallway = True
                t[x][y].blocked = False
                t[x][y].block_sight = False
            if t[x - 1][y].hallway and t[x][y].blocked and t[x + 1][y].hallway:
                t[x][y].hallway = True
                t[x][y].blocked = False
                t[x][y].block_sight = False

    return

    # then punch holes through walls crossing the whole map

    # first veritical walls
    for x in range(1, m.width-1):
        hallway_found = False
        for y in range(1, m.height-1):
            if not t[x][y].blocked:
                hallway_found = True
        if not hallway_found:
            ypos = random.randint(1, m.height - 2)
            t[x][ypos].blocked = False
            t[x][ypos].block_sight = False

    # then horisontal walls
    for y in range(1, m.height-1):
        hallway_found = False
        for x in range(1, m.width-1):
            if not t[x][y].blocked:
                hallway_found = True
        if not hallway_found:
            xpos = random.randint(1, m.width - 2)
            t[xpos][y].blocked = False
            t[xpos][y].block_sight = False


def make_doors(m, chunks):
    for c in chunks:
        dir = random.randint(0, 3)
        xpos = None
        ypos = None
        print("room {} at {}".format(c.room, c))
        if dir == 0:  # up
            xpos = random.randint(c.x + 1, c.x + c.width - 2)
            if c.y == 0:
                ypos = c.y + c.height - 1
            else:
                ypos = c.y
        elif dir == 1:  # right
            if c.x + c.width < m.width:
                xpos = c.x + c.width - 1
            else:
                xpos = c.x
            ypos = random.randint(c.y + 1, c.y + c.height - 2)
        elif dir == 2:  # down
            xpos = random.randint(c.x + 1, c.x + c.width - 2)
            if c.y + c.height < m.height:
                ypos = c.y + c.height - 1
            else:
                ypos = c.y
        elif dir == 3:  # left
            if c.x > 0:
                xpos = c.x
            else:
                xpos = c.x + c.width - 1
            ypos = random.randint(c.y + 1, c.y + c.height - 2)
        assert xpos is not None
        assert ypos is not None
        m.tiles[xpos][ypos].hallway = True
        m.tiles[xpos][ypos].blocked = False
        m.tiles[xpos][ypos].block_sight = False
        m.tiles[xpos][ypos].room = -1


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


class GameMap:
    def __init__(self, size, assets, dungeon_level, constants, monster_chances):
        self.width = size.width
        self.height = size.height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level
        self.assets = assets
        self.entities = []
        self.monster_chances = monster_chances
        self.player_pos = None
        self.make_tower_map(constants)
        assert self.player_pos
        # self.load_map(resource_path("data/maps/test.map"))
        self.tiles = self.set_tile_info(self.tiles)
        # for y in range(self.height):
        #    for x in range(self.width):
        #        print("{:2d}".format(self.tiles[x][y].floor_info), end=",")
        #    print("")

    def initialize_tiles(self):
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def load_map(self, path):
        with open(path, 'r') as reader:
            content = reader.read()
        lines = content.split("\n")
        lines = [line for line in lines if line != ""]
        self.width = len(lines[0])
        self.height = len(lines)
        tiles = self.initialize_tiles()
        for x in range(self.width):
            for y in range(self.height):
                if lines[y][x] == 'P':
                    tiles[x][y].blocked = False
                    tiles[x][y].block_sight = False
                    self.player_pos = Pos(x, y)
                elif lines[y][x] == ' ':
                    tiles[x][y].blocked = False
                    tiles[x][y].block_sight = False
        self.tiles = tiles

    @property
    def free_area(self):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y].hallway:
                    count += 1
        return count

    @property
    def total_size(self):
        return self.width * self.height

    @property
    def first_unused_room_id(self):
        curr = 1
        while True:
            found = False
            for x in range(self.width):
                for y in range(self.height):
                    if self.tiles[x][y].room == curr:
                        found = True
                        break
            if not found:
                break
            else:
                curr += 1
        return curr

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def set_tile_info(self, tiles):
        for x in range(self.width):
            for y in range(self.height):
                if tiles[x][y].blocked:
                    val = 0
                    if y > 0 and tiles[x][y - 1].blocked:  # north
                        val += 1
                    if x < self.width - 1 and tiles[x + 1][y].blocked:  # east
                        val += 2
                    if y < self.height - 1 and tiles[x][y + 1].blocked:  # south
                        val += 4
                    if x > 0 and tiles[x - 1][y].blocked:  # west
                        val += 8
                    tiles[x][y].wall_info = val
                else:
                    val = 0
                    if y > 0 and not tiles[x][y - 1].blocked:  # north
                        val += 1
                    if x < self.width - 1 and not tiles[x + 1][y].blocked:  # east
                        val += 2
                    if y < self.height - 1 and not tiles[x][y + 1].blocked:  # south
                        val += 4
                    if x > 0 and not tiles[x - 1][y].blocked:  # west
                        val += 8
                    tiles[x][y].floor_info = val
        return tiles

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
            packsize = random.randint(1, 3)
            diffs = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 1),
                     (1, -1), (1, 0), (1, 1)]
            clean_diffs = []
            for d in diffs:
                dpos = Pos(x + d[0], y + d[1])
                occupied = False
                for e in self.entities:
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

        num_monsters = random.randint(0, max_monsters_per_room)

        for i in range(num_monsters):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.pos.x == x and entity.pos.y == y]):
                monster_choice = random_choice_from_dict(self.monster_chances)
                entities.extend(self.get_monster(x, y, room, monster_choice))

    def make_map(self, constants):
        rooms = []
        center_of_last_room_x = None
        center_of_last_room_y = None
        for i in range(constants.max_rooms):
            w = random.randint(constants.room_min_size, constants.room_max_size)
            h = random.randint(constants.room_min_size, constants.room_max_size)
            x = random.randint(0, constants.map_size.width - w - 1)
            y = random.randint(0, constants.map_size.height - h - 1)

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

                    if random.randint(0, 1) == 1:
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

    def make_tower_map(self, constants):
        chunks = chunkify(self)
        cleanup_walls(self)
        make_doors(self, chunks)
        px = chunks[0].x + chunks[0].width // 2
        py = chunks[0].y + chunks[0].height // 2
        self.player_pos = Pos(px, py)
        print_map(self)

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
