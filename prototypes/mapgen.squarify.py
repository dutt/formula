import random
import squarify


class tile:
    def __init__(self, wall):
        self.wall = wall
        self.room = -1
        self.symbol = "#" if wall else " "


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[tile(False) for _ in range(height)] for _ in range(width)]


def main():
    m = Map(80, 60)
    total_size = m.width * m.height
    rooms = []
    while sum(rooms) < total_size:
        diff = total_size - sum(rooms)
        if diff > 6:
            roomsize = random.randint(6, min(total_size * 0.5, total_size - sum(rooms)))
            rooms.append(roomsize)
        else:
            rooms[-1] += diff
    print(rooms)

    data = squarify.padded_squarify(rooms, 0, 0, m.width, m.height)
    import json

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
