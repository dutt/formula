from graphics.assets import Assets

class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight
        self.explored = False
        self.wall_info = 0
        self.floor_info = 0
        self.room = -1
        self.hallway = False
        self.symbol = None  # debugging

    def get_drawable(self, visible):
        if visible:
            if self.block_sight: # wall
                return Assets.get().light_wall[self.wall_info]
            else:
                return Assets.get().light_floor[self.floor_info]
        elif self.explored:
            if self.block_sight: # wall
                return Assets.get().dark_wall[self.wall_info]
            else:
                return Assets.get().dark_floor[self.floor_info]
        else:
            return None # not in sight nor explored

    def __repr__(self):
        return str(self)

    def __str__(self):
        attr = ""
        if self.blocked:
            attr += "wall, "
        if self.room != -1:
            attr += "room {}".format(self.room)
        return "<tile {}>".format(attr)
