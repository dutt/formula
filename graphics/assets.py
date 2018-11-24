import pygame

import util
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
from graphics.spritesheet import Spritesheet


class Assets:
    _assets = None

    @staticmethod
    def get():
        return Assets._assets

    def __init__(self):
        if Assets._assets:
            raise Exception("Should only initialize assets once")

        Assets._assets = self

        graphics_file_tile_size = util.Size(16, 16)

        self.reptile_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Reptile0.png"))
        self.wall_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Wall.png"))
        self.undead_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Undead0.png"))
        self.decor_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Decor0.png"))
        self.floor_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Floor.png"))
        self.potion_sheet = Spritesheet(util.resource_path("data/graphics/Items/Potion.png"))
        self.medium_weapons_sheet = Spritesheet(util.resource_path("data/graphics/Items/MedWep.png"))
        self.effect0_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Effect0.png"))

        if graphics_file_tile_size.width != CELL_WIDTH or graphics_file_tile_size.height != CELL_HEIGHT:
            scale = (CELL_WIDTH, CELL_HEIGHT)
        else:
            scale = None

        def get_img(sheet, row, col):
            return sheet.get_image(row, col, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                   scale=scale)
        self.player = get_img(self.reptile_sheet, 1, 1)

        self.stairs = get_img(self.decor_sheet, 2, 9)

        self.light_wall = get_img(self.wall_sheet, 3, 15)
        self.dark_wall = get_img(self.wall_sheet, 3, 21)

        self.light_floor = get_img(self.floor_sheet, 2, 10)
        self.dark_floor = get_img(self.floor_sheet, 2, 14)

        self.ghost = get_img(self.undead_sheet, 2, 2)
        self.demon = get_img(self.undead_sheet, 7, 2)
        self.monster_corpse = get_img(self.decor_sheet, 2, 12)

        self.throwing_bottle = get_img(self.potion_sheet, 0, 0)
        self.sword = get_img(self.medium_weapons_sheet, 0, 0)

        self.shield_effect = get_img(self.effect0_sheet, 4, 23)

        self.font_title = pygame.font.Font(util.resource_path("data/font/joystix.ttf"), 16)
        self.font_message = pygame.font.Font(util.resource_path("data/font/joystix.ttf"), 12)
