from map_related.tile import Tile


class GameMap:
    def __init__(self, size, dungeon_level):
        self.width = size.width
        self.height = size.height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level
        self.entities = []
        self.player_pos = None
        self.tutorial = False
        self.num_keys_found = 0
        self.num_keys_total = 0
        self.stairs_found = False


    def initialize_tiles(self):
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]
        return tiles

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

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    @property
    def num_explored(self):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y].explored:
                    # print("{},{} is explored".format(x, y))
                    count += 1
        return count
