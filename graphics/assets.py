import pygame

import util
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
from graphics.spritesheet import Spritesheet
from graphics import font

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

        self.reptile_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Characters/Reptile"))
        self.dog_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Characters/Dog"))
        self.wall_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Objects/Wall.png"))
        self.undead_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Characters/Undead"))
        self.decor_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Objects/Decor"))
        self.floor_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Objects/Floor.png"))
        self.potion_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Items/Potion.png"))
        self.medium_weapons_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Items/MedWep.png"))
        self.effect_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Objects/Effect"))
        self.ammo_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Items/Ammo.png"))
        self.humanoid_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Characters/Humanoid"))
        self.quadraped_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Characters/Quadraped"))
        self.player_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike/Characters/Player"))
        self.money_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike//Items/Money.png"))
        self.key_sheet = Spritesheet(util.resource_path("data/graphics/DawnLike//Items/Key.png"))

        if graphics_file_tile_size.width != CELL_WIDTH or graphics_file_tile_size.height != CELL_HEIGHT:
            scale = (CELL_WIDTH, CELL_HEIGHT)
        else:
            scale = None

        def get_img(sheet, col, row, rotate=None):
            return sheet.get_image(col, row, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                   scale=scale, rotate=rotate)

        def get_animation(sheet, col, row, rotate=None):
            return sheet.get_animation(col, row, graphics_file_tile_size.width, graphics_file_tile_size.height,
                                       scale=scale, rotate=rotate)

        def get_wall(sheet, col, row):  # col, row are coords of the top left sprite
            retr = []
            retr.append(get_img(sheet, col + 3, row + 0, rotate=  0))  # 0, solo wall
            retr.append(get_img(sheet, col + 1, row + 1, rotate=  0))  # 1, wall to the north
            retr.append(get_img(sheet, col + 1, row + 0, rotate=  0))  # 2, wall to the east
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

        def get_floor(sheet, col, row): # col, row are coords for the top left sprite
            retr = []
            retr.append(get_img(sheet, col + 3, row + 0, rotate=  0))  # 0, solo floor
            retr.append(get_img(sheet, col + 3, row + 2, rotate=  0))  # 1, floor to the north
            retr.append(get_img(sheet, col + 4, row + 1, rotate=  0))  # 2, floor to the east
            retr.append(get_img(sheet, col + 0, row + 2, rotate=  0))  # 3, floor to the north, east
            retr.append(get_img(sheet, col + 1, row + 1, rotate=180))  # 4, floor to the south
            retr.append(get_img(sheet, col + 3, row + 1, rotate=  0))  # 5, floor to the north, south
            retr.append(get_img(sheet, col + 0, row + 0, rotate=  0))  # 6, floor to the east, south
            retr.append(get_img(sheet, col + 0, row + 1, rotate=  0))  # 7, floor to the north, south, east
            retr.append(get_img(sheet, col + 6, row + 1, rotate=  0))  # 8, floor to the west
            retr.append(get_img(sheet, col + 2, row + 2, rotate=  0))  # 9, floor to the north, west
            retr.append(get_img(sheet, col + 5, row + 1, rotate=  0))  # 10, floor to the east, west
            retr.append(get_img(sheet, col + 1, row + 2, rotate=  0))  # 11, floor to the north, east, west
            retr.append(get_img(sheet, col + 2, row + 0, rotate=  0))  # 12, floor to the south, west
            retr.append(get_img(sheet, col + 2, row + 1, rotate=  0))  # 13, floor to the north, south, west
            retr.append(get_img(sheet, col + 1, row + 0, rotate=  0))  # 14. floor to the east, south, west
            retr.append(get_img(sheet, col + 1, row + 1, rotate=  0))  # 15, floor all around
            return retr

        self.player = get_animation(self.player_sheet, 1, 0)

        self.stairs = get_img(self.decor_sheet, 2, 9)

        self.light_wall = get_wall(self.wall_sheet, 0, 3)
        self.dark_wall = get_wall(self.wall_sheet, 0, 6)

        self.light_floor = get_floor(self.floor_sheet, 0, 6)
        self.dark_floor = get_floor(self.floor_sheet, 0, 9)

        self.monster_corpse = get_img(self.decor_sheet, 2, 12)

        self.ghost = get_animation(self.undead_sheet, 2, 2)
        self.demon = get_animation(self.undead_sheet, 7, 2)
        self.chucker = get_animation(self.humanoid_sheet, 2, 12)
        self.wolf = get_animation(self.quadraped_sheet, 5, 0)

        self.thug = get_animation(self.humanoid_sheet, 0, 0)
        self.mercenary = get_animation(self.humanoid_sheet, 0, 4)
        self.stalker = get_animation(self.humanoid_sheet, 4, 7)

        self.dog = get_animation(self.quadraped_sheet, 6, 0)
        self.boar = get_animation(self.quadraped_sheet, 3, 0)
        self.armored_bear = get_animation(self.quadraped_sheet, 7, 0)

        self.axe_thrower = get_animation(self.humanoid_sheet, 0, 5)
        self.rifleman = get_animation(self.humanoid_sheet, 5, 2)
        self.zapper = get_animation(self.humanoid_sheet, 3, 12)

        self.boss = get_animation(self.undead_sheet, 0, 8)

        self.throwing_bottle = get_img(self.potion_sheet, 0, 0)
        self.sword = get_img(self.medium_weapons_sheet, 0, 0)
        self.arrow = get_img(self.ammo_sheet, 0, 2)

        self.shield_effect = get_animation(self.effect_sheet, 4, 23)
        self.spark_effect = get_animation(self.effect_sheet, 3, 24)

        self.crystal = get_img(self.money_sheet, 1, 3)
        self.key = get_img(self.key_sheet, 0, 0)

        self.font_title = pygame.font.Font(util.resource_path("data/font/CutiveMono-Regular.ttf"), 20)
        #self.font_message = pygame.font.Font(util.resource_path("data/font/joystix.ttf"), 14)
        #self.font_message = pygame.font.Font(util.resource_path("data/font/CutiveMono-Regular.ttf"), 16)

        self.font_message = pygame.font.Font(util.resource_path("data/font/rm_typerighter_old.ttf"), 38)
        self.font_message_height = font.get_height(self.font_message)
        #self.font_message = pygame.font.Font(util.resource_path("data/font/primer print.ttf"), 30)
