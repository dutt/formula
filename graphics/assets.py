import pygame

import util
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
from graphics.spritesheet import Spritesheet


class Assets:
    def __init__(self):
        graphics_file_tile_size = util.Size(16, 16)

        self.reptile_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Reptile0.png"))
        self.wall_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Wall.png"))
        self.undead_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Undead0.png"))
        self.decor_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Decor0.png"))
        self.floor_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Floor.png"))

        if graphics_file_tile_size.width != CELL_WIDTH or graphics_file_tile_size.height != CELL_HEIGHT:
            scale = (CELL_WIDTH, CELL_HEIGHT)
        else:
            scale = None

        self.player = self.reptile_sheet.get_image(1, 1, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                                   scale=scale)

        self.stairs = self.decor_sheet.get_image(2, 9, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                                 scale=scale)

        self.light_wall = self.wall_sheet.get_image(3, 15, graphics_file_tile_size.width,
                                                    graphics_file_tile_size.height,
                                                    scale=scale)
        self.dark_wall = self.wall_sheet.get_image(3, 21, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                                   scale=scale)

        self.light_floor = self.floor_sheet.get_image(2, 10, graphics_file_tile_size.width,
                                                      graphics_file_tile_size.height,
                                                      scale=scale)
        self.dark_floor = self.floor_sheet.get_image(2, 14, graphics_file_tile_size.width,
                                                     graphics_file_tile_size.height,
                                                     scale=scale)

        self.ghost = self.undead_sheet.get_image(2, 2, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                                 scale=scale)
        self.demon = self.undead_sheet.get_image(7, 2, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                                 scale=scale)
        self.monster_corpse = self.decor_sheet.get_image(2, 12, graphics_file_tile_size.width,
                                                         graphics_file_tile_size.height,
                                                         scale=scale)

        self.font_title = pygame.font.Font(util.resource_path("data/font/joystix.ttf"), 16)
        self.font_message = pygame.font.Font(util.resource_path("data/font/joystix.ttf"), 12)
