from graphics.spritesheet import Spritesheet
import util

class Assets:
    def __init__(self):
        self.load_assets()

    def load_assets(self):
        self.reptile_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Reptile0.png"))
        self.wall_sheet = Spritesheet(util.resource_path("data/graphics/Objects/Wall.png"))
        self.undead_sheet = Spritesheet(util.resource_path("data/graphics/Characters/Undead0.png"))

        #self.player = self.reptile_sheet.get_animation(15, 5, 16, 16, 2, (32, 32))
        self.player = self.reptile_sheet.get_image(1, 1, 16, 16)

        self.light_wall = self.wall_sheet.get_image(3, 15)
        self.dark_wall = self.wall_sheet.get_image(3, 21)

        self.ghost = self.undead_sheet.get_image(2, 2)
        self.demon = self.undead_sheet.get_image(7, 2)
