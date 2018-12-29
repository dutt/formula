import math
import random
import sys
from collections import defaultdict

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


def make_rooms(origins, map):
    def queue_not_empty():
        for o in origins:
            if len(queues[o]) > 0:
                return True
        return False

    def get_children(node):
        check = []
        if node.x > 0:
            check.append(Pos(node.x - 1, node.y))
        if node.x < map.width - 1:
            check.append(Pos(node.x + 1, node.y))
        if node.y > 0:
            check.append(Pos(node.x, node.y - 1))
        if node.y < map.height - 1:
            check.append(Pos(node.x, node.y + 1))
        clean = []
        for c in check:
            if map.tiles[c.x][c.y].room != -1:
                continue
            if map.tiles[c.x][c.y].blocked:
                continue
            queued = False
            for o in origins:
                q = queues[o]
                if c in q:
                    queued = True
                    break
            if not queued:
                # print("{}: {} is clean".format(o, c))
                clean.append(c)
        return clean

    visited = {}
    queues = {}
    for o in origins:
        visited[o] = set()
        queues[o] = list([o])
    while queue_not_empty():
        for idx, o in enumerate(origins):
            if len(queues[o]) == 0:
                # print("Orig {} is done".format(idx))
                continue
            pos = queues[o].pop(0)
            # print("{}: popped {}".format(idx, pos))
            # print(pos)
            if map.tiles[pos.x][pos.y].room != -1:
                continue  # room already marked
            visited[o].add(pos)
            # print("Marking {} as room {}".format(pos, idx))
            map.tiles[pos.x][pos.y].room = idx
            children = get_children(pos)
            for child in children:
                queues[o].append(child)
        # for idx, o in enumerate(origins):
        #    print("queue for origin {}".format(o))
        #    for p in queues[o]:
        #        print("\t{}".format(p))
        # print_map(map)
        # print("-")
    return visited


def make_walls(m):
    tiles = m.tiles
    for x in range(0, m.width):
        for y in range(0, m.height):
            if x > 0 and tiles[x - 1][y].room != tiles[x][y].room:
                tiles[x][y].blocked = True
                tiles[x][y].block_sight = True
            if y > 0 and tiles[x][y - 1].room != tiles[x][y].room:
                tiles[x][y].blocked = True
                tiles[x][y].block_sight = True

            tiles[0][y].blocked = True
            tiles[0][y].block_sight = True

            tiles[m.width - 1][y].blocked = True
            tiles[m.width - 1][y].block_sight = True

        tiles[x][0].blocked = True
        tiles[x][0].block_sight = True
        tiles[x][m.height - 1].blocked = True
        tiles[x][m.height - 1].block_sight = True

    # fix up left  - down right diagonals
    for x in range(0, m.width - 1):
        for y in range(0, m.height - 1):
            if tiles[x][y].blocked and tiles[x + 1][y + 1].blocked:
                tiles[x + 1][y].blocked = True
                tiles[x + 1][y].block_sight = True

    # fix up right- down left diagonals
    for x in range(0, m.width - 1):
        for y in range(1, m.height):
            if tiles[x][y].blocked and tiles[x + 1][y - 1].blocked:
                tiles[x][y - 1].blocked = True
                tiles[x][y - 1].block_sight = True


def dist(pos, dest):
    dx = pos.x - dest.x
    dy = pos.y - dest.y
    return math.sqrt(dx ** 2 + dy ** 2)


def check_path(m, src, dest):
    def get_next(queue, fscore):
        min_val = sys.maxsize
        min_obj = None
        for p in queue:
            if fscore[p] < min_val:
                min_obj = p
                min_val = fscore[p]
        return min_obj

    def get_neighbours(p, queue, visited):
        retr = []
        if p.x > 0:
            retr.append(Pos(p.x - 1, p.y))
        if p.x < m.width - 1:
            retr.append(Pos(p.x + 1, p.y))
        if p.y > 0:
            retr.append(Pos(p.x, p.y - 1))
        if p.y < m.height - 1:
            retr.append(Pos(p.x, p.y + 1))
        clean = []
        for r in retr:
            if m.tiles[r.x][r.y].blocked:
                continue
            if r in queue:
                continue
            if r in visited:
                continue
            clean.append(r)
        return clean

    def reconstruct(from_path, target):
        n = from_path[target]
        path = [target]
        while n != src:
            path.append(n)
            n = from_path[n]
        path.append(src)
        return path

    #print("searching from {} to {}".format(src, dest))
    visisted = []
    queue = [src]
    # total cost to that node from start
    gscore = defaultdict(lambda: sys.maxsize)
    gscore[src] = 0
    # total cost for path through that node
    fscore = defaultdict(lambda: sys.maxsize)
    fscore[src] = dist(src, dest)
    from_path = {}
    while len(queue) > 0:
        for p in queue:
            pass
            #print("{}, f={}".format(p, fscore[p]))
        p = get_next(queue, fscore)
        m.tiles[p.x][p.y].symbol = '.'
        #print("next {} with fscore {}".format(p, fscore[p]))
        if p == dest:
            return True # reconstruct(from_path, dest)
        queue.remove(p)
        visisted.append(p)

        neighbours = get_neighbours(p, queue, visisted)
        for n in neighbours:
            tentantive_g = gscore[p] + 1
            if tentantive_g >= gscore[n]:
                continue
            gscore[n] = tentantive_g
            fscore[n] = tentantive_g + dist(n, dest)
            queue.insert(0, n)
            #print("adding neighbour {}".format(n))
            from_path[n] = p
    return False
    closest_node = None
    min_dist = sys.maxsize
    for n in from_path:
        d = dist(n, dest)
        if d < min_dist:
            closest_node = n
            min_dist = d
    return False


def get_pairs(origins):
    retr = []
    for o1 in origins:
        for o2 in origins:
            if o1 == o2:
                continue
            p1 = (o1, o2)
            p2 = (o2, o1)
            if p1 not in retr and p2 not in retr:
                retr.append(p1)
    return retr


import itertools


def make_doors(m, origins, paths):
    def validate():
        failures = 0
        pairs = get_pairs(origins)
        for p in pairs:
            o1, o2 = p
            valid = check_path(m, o1, o2)
            if not valid:
                failures += 1
        return failures

    def two_tiles_from_diff_rooms():
        pairs = get_pairs(origins)
        p = random.choice(pairs)
        a, b = p
        first = None
        while not first:
            x = random.randint(1, m.width - 2)
            y = random.randint(1, m.height - 2)
            if m.tiles[x][y].room == m.tiles[a.x][a.y].room and m.tiles[x][y].room != -1 and not m.tiles[x][y].blocked:
                first = Pos(x, y)
        second = None
        while not second:
            x = random.randint(1, m.width - 2)
            y = random.randint(1, m.height - 2)
            if m.tiles[x][y].room == m.tiles[b.x][b.y].room and m.tiles[x][y].room != -1 and not m.tiles[x][y].blocked:
                second = Pos(x, y)
        return first, second

    current_failures = len(origins)
    while current_failures > 0:
        first, second = two_tiles_from_diff_rooms()
        from util import get_line
        line = get_line(first.tuple(), second.tuple())
        for idx, p in enumerate(line):
            if idx > 0:
                prev = line[idx - 1]
            else:
                prev = p
            x, y = p
            px, py = prev
            if x != px and y != py:  # diagonal step
                m.tiles[x][py].blocked = False
                m.tiles[x][py].block_sight = False
                # print("Clearing {}, {}".format(x, py))
            m.tiles[x][y].blocked = False
            m.tiles[x][y].block_sight = False
            # print("Clearing {}, {}".format(x, y))
        #print_map(m, room_ids=False, extra_points=[first, second])
        print_map(m, room_ids=False, extra_points=origins)
        print("origins {}".format(origins))
        current_failures = validate()
        print("failures {}".format(current_failures))


def make_doors2(m, origins, paths):
    def get_wall(attempted, count):
        flat = list(itertools.chain.from_iterable(paths))
        tiles = []
        random.shuffle(flat)

        retr = []
        for pos in flat:
            tiles.append((pos, m.tiles[pos.x][pos.y]))
            # x = random.randint(0, m.width - 1)
            # y = random.randint(0, m.height - 1)
            # print("pos {}, attempted {}".format(pos, attempted))
            if m.tiles[pos.x][pos.y].blocked and pos not in attempted and len(retr) < count:
                retr.append(pos)

        # pairs = get_pairs(origins)
        # for p in pairs:
        #    src, dst = p
        #    for x in range(src.x, dst.x):
        #        for y in range(src.y, dst.y):
        #            if not m.tiles[x][y].blocked:
        #                continue
        #            return Pos(x, y)

        # raise Exception("No wall found")
        return retr

    def validate():
        failures = 0
        pairs = get_pairs(origins)
        for p in pairs:
            o1, o2 = p
            valid = check_path(m, o1, o2)
            if not valid:
                failures += 1
        return failures

    current_failures = validate()
    attempted = []
    count = 1
    while current_failures > 0:
        possible_removed = get_wall(attempted, count)
        if not possible_removed:
            count += 1
            attempted = []
            continue
        attempted.extend(possible_removed)
        # print(possible_removed)
        for pr in possible_removed:
            m.tiles[pr.x][pr.y].blocked = False
            m.tiles[pr.x][pr.y].block_sight = False
        possible_valid_count = validate()
        if possible_valid_count == current_failures:  # removing a wall added a valid path
            for pr in possible_removed:
                m.tiles[pr.x][pr.y].blocked = True
                m.tiles[pr.x][pr.y].block_sight = True
        else:
            current_failures = possible_valid_count


def print_map(m, room_ids=True, walls=True, extra_points=[]):
    for y in range(m.height):
        for x in range(m.width):
            if m.tiles[x][y].blocked and walls:
                print("#", end="")
            elif m.tiles[x][y].room != -1 and room_ids:
                print(m.tiles[x][y].room, end="")
            elif Pos(x, y) in extra_points:
                print("X", end="")
            elif m.tiles[x][y].symbol:
                print(m.tiles[x][y].symbol, end="")
            else:
                print(" ", end="")
            # print(m.tiles[x][y].room if m.tiles[x][y].room != -1 else ' ', end="")
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
        self.player_pos = None
        self.monster_chances = monster_chances
        self.make_tower_map(constants)
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
        def make_origins():
            origins = []
            attempts = 0
            rooms = random.randint(2, constants.max_rooms)
            min_dist = (constants.map_size.width + constants.map_size.height) * 0.1
            while len(origins) < rooms:
                attempts += 1
                if attempts > 100:
                    break
                x = random.randint(1, constants.map_size.width - 2)
                y = random.randint(1, constants.map_size.height - 2)
                newpos = Pos(x, y)
                too_close = False
                for current in origins:
                    if dist(newpos, current) < min_dist:
                        too_close = True
                if too_close:
                    continue
                origins.append(Pos(x, y))
            return origins

        origins = make_origins()

        paths = []
        #for p in get_pairs(origins):
        #    p1, p2 = p
        #    path = check_path(self, p1, p2)
        #    paths.append(path)

        make_rooms(origins, self)
        print("Rooms")
        # print_map(self)
        make_walls(self)
        print("Walls")
        # print_map(self)
        make_doors(self, origins, paths)
        print("Doors")
        # print_map(self)
        self.player_pos = origins[0]

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
