from map_related.tile import Tile

"""
class BasicMapGenerator(MapGenerator):

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

    def place_monsters(self):
        # done earlier
        pass

    def place_stairs(self):
        # done earlier
        pass

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level + 1)

        num_monsters = random.randint(0, max_monsters_per_room)

        for i in range(num_monsters):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.pos.x == x and entity.pos.y == y]):
                monster_choice = random_choice_from_dict(self.monster_chances)
                entities.extend(self.get_monster(x, y, room, monster_choice))

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
"""

class GameMap:
    def __init__(self, size, dungeon_level):
        self.width = size.width
        self.height = size.height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level
        self.entities = []
        self.player_pos = None
        # self.load_map(resource_path("data/maps/test.map_related"))
        # self.tiles = self.set_tile_info(self.tiles)
        # for y in range(self.height):
        #    for x in range(self.width):
        #        print("{:2d}".format(self.tiles[x][y].floor_info), end=",")
        #    print("")

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
