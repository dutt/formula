from enum import Enum, auto


def print_map(m):
    for y in range(m.height):
        for x in range(m.width):
            if m.tiles[x][y].wall:
                print("##", end="")
            elif m.tiles[x][y].room != -1:
                print("{:2}".format(m.tiles[x][y].room), end="")
            elif m.tiles[x][y].hallway:
                print("--", end="")
            else:
                print(" ", end="")
            # print(m.tiles[x][y].room if m.tiles[x][y].room != -1 else ' ', end="")
        print("")
    print("")


class TileType(Enum):
    Room = auto()
    Hallway = auto()
    Door = auto()


class tile:
    def __init__(self, wall):
        self.wall = wall
        self.type = TileType.Room
        self.room = -1
        self.hallway = False
        self.symbol = "#" if wall else " "


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[tile(False) for _ in range(height)] for _ in range(width)]

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


class Dir(Enum):
    horizontal = auto()
    vertical = auto()


from util import Rect

import random


def mark_room(m, chunk, room):
    for x in range(chunk.x, chunk.x + chunk.width):
        for y in range(chunk.y, chunk.y + chunk.height):
            m.tiles[x][y].hallway = False
            m.tiles[x][y].room = room
        m.tiles[x][chunk.y].wall = True
        m.tiles[x][chunk.y + chunk.height - 1].wall = True
    for y in range(chunk.y, chunk.y + chunk.height):
        m.tiles[chunk.x][y].wall = True
        m.tiles[chunk.x + chunk.width - 1][y].wall = True
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
    start_chunk.room = -1
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
    for x in range(1, m.width - 1):
        for y in range(1, m.height - 1):
            if t[x][y - 1].hallway and t[x][y].wall and t[x][y + 1].hallway:
                t[x][y].hallway = True
                t[x][y].wall = False
            if t[x - 1][y].hallway and t[x][y].wall and t[x + 1][y].hallway:
                t[x][y].hallway = True
                t[x][y].wall = False


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
        m.tiles[xpos][ypos].wall = False
        m.tiles[xpos][ypos].room = -1


def main():
    import datetime

    now = datetime.datetime.now()
    txt = str(now)
    txt = "2018-12-30 09:38:04.303108"
    print("Using seed: <{}>".format(txt))
    import random

    random.seed(txt)

    m = Map(80, 60)
    chunks = chunkify(m)
    cleanup_walls(m)
    make_doors(m, chunks)
    print_map(m)


if __name__ == "__main__":
    main()
