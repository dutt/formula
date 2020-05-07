import os, glob

import pygame

import graphics.constants as constants


class Spritesheet:
    def __init__(self, path):
        if os.path.exists(path):  # single sheet
            self.sheets = [pygame.image.load(path).convert()]
        else:  # numbered sheets
            files = glob.glob(path + "*")
            files = sorted(files)
            if not files:
                raise FileNotFoundError("{} doesn't exist".format(path))
            self.sheets = [pygame.image.load(f).convert() for f in files]

    def get_image(
        self, col, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, scale=None, rotate=None, sheet=None,
    ):
        if not sheet:
            sheet = self.sheets[0]
        image = pygame.Surface((width, height))
        image.blit(sheet, (0, 0), (col * width, row * height, width, height))
        image.set_colorkey(constants.colors.BLACK)
        if scale:
            new_w, new_h = scale
            image = pygame.transform.scale(image, (new_w, new_h))
        if rotate:
            image = pygame.transform.rotate(image, rotate)
        image.convert()
        image.set_alpha(255)
        return [image]

    def get_animation(
        self, col, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, scale=None, rotate=None,
    ):
        images = []
        for sheet in self.sheets:
            images.extend(self.get_image(col, row, width, height, scale, rotate, sheet))
        return images
