import pygame

import graphics.constants as constants


class Spritesheet():
    def __init__(self, path):
        self.sheet = pygame.image.load(path).convert()

    def get_image(self, col, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, scale=None):
        image = pygame.Surface((width, height))
        image.blit(self.sheet, (0, 0), (col * width, row * height, width, height))
        image.set_colorkey(constants.colors.BLACK)
        if scale:
            new_w, new_h = scale
            image = pygame.transform.scale(image, (new_w, new_h))
        image.convert()
        image.set_alpha(255)
        return [image]

    def get_animation(self, col, row, width=constants.CELL_WIDTH, height=constants.CELL_HEIGHT, num_sprites=1,
                      scale=None):
        images = []
        for i in range(num_sprites):
            image = pygame.Surface((width, height))
            image.blit(self.sheet, (0, 0), (col * width + width * i, row * height, width, height))
            image.set_colorkey(constants.colors.BLACK)

            if scale:
                new_w, new_h = scale
                image = pygame.transform.scale(image, (new_w, new_h))

            images.append(image)
        return images
