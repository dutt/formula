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
