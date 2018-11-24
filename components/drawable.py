import pygame


class Drawable():
    def __init__(self, asset):
        self.asset = asset
        self.orig = asset

    def colorize(self, colour):
        img = self.orig[0].copy()
        #img.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        img.fill(colour[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
        img.set_colorkey(colour)
        self.asset = [img]

    def restore(self):
        self.asset = self.orig
