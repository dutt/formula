import cmath
import math
import random

import pytest

from util import Pos


class tile:
    def __init__(self, wall):
        self.wall = wall
        self.room = -1
        self.symbol = "#" if wall else " "


class Map:
    def __init__(self, width, height, radius, rooms):
        self.width = width
        self.height = height
        self.radius = radius
        self.rooms = rooms
        self.tiles = [[tile(False) for _ in range(height)] for _ in range(width)]


def make_circular(m):
    cx = m.width // 2
    cy = m.height // 2
    for x in range(m.width):
        for y in range(m.height):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if m.radius - 0.5 < dist < m.radius + 0.5:
                m.tiles[x][y].wall = True
    return m


from enum import Enum, auto


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


def make_improved_recursive_division(map):
    region = []
    for x in range(map.width):
        for y in range(map.height):
            region.append(Pos(x, y))

    def get_point_in_region(region):
        while True:
            x = random.randint(0, map.width)
            y = random.randint(0, map.height)
            if (x, y) in region:
                return Pos(x, y)

    def flood(region, points):
        def has_unfilled_cells(region):
            for p in region:
                if p.room == -1:
                    return True
            return False

        # clear point room assignments
        for p in region:
            p.room = -1
        while region.expand():
            pass

    p1 = get_point_in_region(region)
    p2 = get_point_in_region(region)
    map.tiles[p1.x][p1.y].symbol = "1"
    map.tiles[p2.x][p2.y].symbol = "2"
    return map


def cart2pol(x, y):
    # rho = math.hypot(x, y)
    # phi = math.atan2(x, y)
    # return rho, phi
    c = complex(x, y)
    r, phi = cmath.polar(c)
    return r, phi


def pol2cart(rho, phi):
    x = rho * math.cos(phi)
    y = rho * math.sin(phi)
    return x, y


def get_centers(map, count):
    retr = []

    return retr


def test(x, y):
    r, p = cart2pol(x, y)
    x2, y2 = pol2cart(r, p)
    pytest.approx(x, x2)
    pytest.approx(y, y2)


class Region2:
    def __init__(self, origin, map, id):
        self.origin = origin
        self.points = [self.origin]
        self.map = map
        self.map.tiles[origin.x][origin.y].room = id
        self.id = id
        self.last_p = None
        self.last_dir = None

    def expand(self):
        def next(orig, prev, direction, n):
            if direction == Direction.RIGHT:
                if prev.x < orig.x + n and prev.x < self.map.width - 1:
                    return Pos(prev.x + 1, prev.y), Direction.RIGHT
                elif prev.y < self.map.height - 1:
                    return Pos(prev.x, prev.y + 1), Direction.DOWN
            elif direction == Direction.DOWN:
                if prev.y < orig.y + n and prev.y < self.map.height - 1:
                    return Pos(prev.x, prev.y + 1), Direction.DOWN
                elif prev.x > 0:
                    return Pos(prev.x - 1, prev.y), Direction.LEFT
            elif direction == Direction.LEFT:
                if prev.x > orig.x - n and prev.x > 0:
                    return Pos(prev.x - 1, prev.y), Direction.LEFT
                elif prev.y > 0:
                    return Pos(prev.x, prev.y - 1), Direction.UP
            elif direction == Direction.UP:
                if prev == orig:
                    return None, None
                elif prev.y > 0:
                    return Pos(prev.x, prev.y - 1), Direction.UP
            return None, None

        n = 1
        full = False
        found = False
        if self.last_p:
            p = self.last_p
            direction = self.last_dir
        else:
            p = Pos(-n, -n) + self.origin
            direction = Direction.RIGHT
        start = self.origin
        while not full and not found:
            p, direction = next(start, p, direction, n)
            # print("p {}, dir {}".format(p, direction))
            if not p:
                #    print("end")
                self.last_dir = self.last_p = None
                return False
            if self.map.tiles[p.x][p.y].room == -1:
                #    print("set {}".format(p))
                self.map.tiles[p.x][p.y].room = self.id
                self.last_p = p
                self.last_dir = direction
                return True
            elif p == start and dir == Direction.UP:
                self.last_dir = self.last_p = None
                return False


def BFS(origins, map):
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
            if map.tiles[c.x][c.y].wall:
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
                tiles[x][y].wall = True
            if y > 0 and tiles[x][y - 1].room != tiles[x][y].room:
                tiles[x][y].wall = True


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
            if m.tiles[r.x][r.y].wall:
                continue
            if r in queue:
                continue
            if r in visited:
                continue
            clean.append(r)
        return clean

    def reconstruct(from_path):
        n = from_path[dest]
        path = [dest]
        while n != src:
            path.append(n)
            n = from_path[n]
        path.append(src)
        return path

    visisted = []
    queue = [src]
    gscore = defaultdict(lambda: sys.maxsize)
    gscore[src] = 0
    fscore = defaultdict(lambda: sys.maxsize)
    fscore[src] = dist(src, dest)
    from_path = {}
    while len(queue) > 0:
        p = get_next(queue, fscore)
        if p == dest:
            return reconstruct(from_path)
        queue.remove(p)
        visisted.append(p)

        neighbours = get_neighbours(p, queue, visisted)
        for n in neighbours:
            tentantive_f = fscore[p] + dist(p, n)
            if tentantive_f >= fscore[n]:
                continue
            gscore[n] = tentantive_f
            fscore[n] = tentantive_f + dist(n, dest)
            queue.append(n)
            from_path[n] = p
    return False


import sys
from collections import defaultdict
import itertools


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


def make_doors(m, origins, paths):
    def get_wall(attempted):
        flat = list(itertools.chain.from_iterable(paths))
        while True:
            # x = random.randint(0, m.width - 1)
            # y = random.randint(0, m.height - 1)
            pos = random.choice(flat)
            if m.tiles[pos.x][pos.y].wall and pos not in attempted:
                return pos

    def validate():
        failures = 0
        pairs = get_pairs(origins)
        for p in pairs:
            o1, o2 = p
            if o1 == o2:
                continue
            if not check_path(m, o1, o2):
                failures += 1
        return failures

    current_failures = validate()
    attempted = []
    while current_failures > 0:
        possible_removed = get_wall(attempted)
        attempted.append(possible_removed)
        print(possible_removed)
        m.tiles[possible_removed.x][possible_removed.y].wall = False
        possible_valid_count = validate()
        if possible_valid_count == current_failures:  # removing a wall added a valid path
            m.tiles[possible_removed.x][possible_removed.y].wall = True
        current_failures = possible_valid_count


def print_map(m):
    for y in range(m.height):
        for x in range(m.width):
            if m.tiles[x][y].wall:
                print("#", end="")
            # elif m.tiles[x][y].room != -1:
            #    print(m.tiles[x][y].room, end="")
            else:
                print(" ", end="")
            # print(m.tiles[x][y].room if m.tiles[x][y].room != -1 else ' ', end="")
        print("")
    print("")


def main():
    w = 3
    h = 6
    r = 8
    w = 40
    h = 40
    m = Map(w, h, r, 3)
    # m = make_circular(m)
    rooms = random.randint(2, 4)
    min_dist = (w + h) / 4
    origins = []
    attempts = 0
    while len(origins) < rooms:
        attempts += 1
        if attempts > 100:
            break
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        newpos = Pos(x, y)
        too_close = False
        for current in origins:
            if dist(newpos, current) < min_dist:
                too_close = True
        if too_close:
            continue
        origins.append(Pos(x, y))
    print("origins {}".format(origins))
    # m = make_improved_recursive_division(m)
    # r1 = Region(Pos(0, 0), m, 1)
    # r2 = Region(Pos(1, 3), m, 2)
    # run = True
    # while run:
    #    if not r1.expand() and not r2.expand():
    #        run = False
    # test(1, 2)
    # test(2, 1)
    # test(16.5, 4.2)
    # origins = [Pos(10, 6), Pos(10, 14)]
    # origins = [Pos(1, 1), Pos(1, 4)]
    # origins = [Pos(1, 0), Pos(1,3)]
    BFS(origins, m)
    # print("clear")
    # print_map(m)
    paths = []
    for p in get_pairs(origins):
        p1, p2 = p
        path = check_path(m, p1, p2)
        paths.append(path)

    make_walls(m)
    print("walled")
    print_map(m)
    print("doored")
    make_doors(m, origins, paths)
    # for x in range(m.width):
    #    m.tiles[x][1].wall = True
    # print(check_path(m, Pos(0, 0), Pos(2, 4)))
    print_map(m)

    room_centers = get_centers(m, 4)


if __name__ == "__main__":
    main()
