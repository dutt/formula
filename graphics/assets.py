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
        self.ammo_sheet = Spritesheet(util.resource_path("data/graphics/Items/Ammo.png"))
        self.humanoid_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Humanoid0.png"))
        self.quadraped_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Quadraped0.png"))

        if graphics_file_tile_size.width != CELL_WIDTH or graphics_file_tile_size.height != CELL_HEIGHT:
            scale = (CELL_WIDTH, CELL_HEIGHT)
        else:
            scale = None

        def get_img(sheet, col, row, rotate=None):
            return sheet.get_image(col, row, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                   scale=scale, rotate=rotate)

        def get_wall(sheet, col, row):  # row, col for the coord of the top left sprite
            retr = []
            retr.append(get_img(sheet, col + 3, row + 0, rotate=  0))  # 0, solo wall
            retr.append(get_img(sheet, col + 1, row + 1, rotate=  0))  # 1, wall to the north
            retr.append(get_img(sheet, col + 1, row + 1, rotate= 90))  # 2, wall to the east
            retr.append(get_img(sheet, col + 0, row + 2, rotate=  0))  # 3, wall to the north, east
            retr.append(get_img(sheet, col + 1, row + 1, rotate=180))  # 4, wall to the south
            retr.append(get_img(sheet, col + 0, row + 1, rotate=  0))  # 5, wall to the north, south
            retr.append(get_img(sheet, col + 0, row + 0, rotate=  0))  # 6, wall to the east, south
            retr.append(get_img(sheet, col + 3, row + 1, rotate=  0))  # 7, wall to the north, south, east
            retr.append(get_img(sheet, col + 1, row + 0, rotate=  0))  # 8, wall to the west
            retr.append(get_img(sheet, col + 2, row + 2, rotate=  0))  # 9, wall to the north, west
            retr.append(get_img(sheet, col + 1, row + 0, rotate=  0))  # 10, wall to the east, west
            retr.append(get_img(sheet, col + 4, row + 2, rotate=  0))  # 11, wall to the north, east, west
            retr.append(get_img(sheet, col + 2, row + 0, rotate=  0))  # 12, wall to the south, west
            retr.append(get_img(sheet, col + 5, row + 1, rotate=  0))  # 13, wall to the north, south, west
            retr.append(get_img(sheet, col + 4, row + 0, rotate=  0))  # 14. wall to the east, south, west
            retr.append(get_img(sheet, col + 4, row + 1, rotate=  0))  # 15, wall to everywhere
            return retr

        self.player = get_img(self.reptile_sheet, 1, 1)

        self.stairs = get_img(self.decor_sheet, 2, 9)

        self.light_wall = get_wall(self.wall_sheet, 0, 3)
        self.dark_wall = get_wall(self.wall_sheet, 0, 6)

        self.light_floor = get_img(self.floor_sheet, 2, 10)
        self.dark_floor = get_img(self.floor_sheet, 2, 14)

        self.ghost = get_img(self.undead_sheet, 2, 2)
        self.demon = get_img(self.undead_sheet, 7, 2)
        self.monster_corpse = get_img(self.decor_sheet, 2, 12)
        self.chucker = get_img(self.humanoid_sheet, 2, 12)
        self.wolf = get_img(self.quadraped_sheet, 5, 0)

        self.throwing_bottle = get_img(self.potion_sheet, 0, 0)
        self.sword = get_img(self.medium_weapons_sheet, 0, 0)
        self.arrow = get_img(self.ammo_sheet, 0, 2)

        self.shield_effect = get_img(self.effect0_sheet, 4, 23)
        self.spark_effect = get_img(self.effect0_sheet, 3, 24)

        self.font_title = pygame.font.Font(util.resource_path("data/font/joystix.ttf"), 16)
        self.font_message = pygame.font.Font(util.resource_path("data/font/joystix.ttf"), 12)
