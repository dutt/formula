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

    def __repr__(self):
        return str(self)

    def __str__(self):
        attr = ""
        if self.blocked:
            attr += "wall, "
        if self.room != -1:
            attr += "room {}".format(self.room)
        return "<tile {}>".format(attr)
