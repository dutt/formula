from util import Size


class Camera:
    def __init__(self, width, height, game_data):
        self.x1 = 0
        self.y1 = 0
        self.x2 = width
        self.y2 = height
        self.width = width
        self.height = height
        self.orig_width = width
        self.orig_height = height
        self.game_data = game_data
        self.map_size = None

    def initialize_map(self):
        assert self.game_data
        self.map_size = Size(self.game_data.map.width, self.game_data.map.height)
        self.width = min(self.map_size.width, self.width)
        self.height = min(self.map_size.height, self.height)

    def center_on(self, x, y):
        assert self.map_size
        if x < self.width / 2:
            self.x1 = 0
            self.x2 = min(self.width, self.map_size.width)
        elif x >= self.map_size.width - self.width // 2:
            self.x1 = max(0, self.map_size.width - self.width - 1)
            self.x2 = self.map_size.width
        else:
            self.x1 = x - self.width // 2
            self.x2 = x + 1 + self.width // 2

        if y < self.height / 2:
            self.y1 = 0
            self.y2 = min(self.height, self.map_size.height)
        elif y >= self.map_size.height - self.height // 2:
            self.y1 = max(0, self.map_size.height - self.height - 1)
            self.y2 = self.map_size.height
        else:
            self.y1 = y - self.height // 2
            self.y2 = y + 1 + self.height // 2

    def map_to_screen(self, x, y):
        sx = x - self.x1
        sy = y - self.y1
        return sx, sy

    def screen_to_map(self, x, y):
        sx = self.x1 + x
        sy = self.y1 + y
        return sx, sy
