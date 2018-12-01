import pygame


class Drawable():
    def __init__(self, asset):
        super().__init__()
        self.asset_ = asset
        self.orig = asset
        self.curr_idx = 0
        self.flickerspeed = 1 #change once per second
        self.flickertimer = 0

    def colorize(self, colour, mode=pygame.BLEND_RGBA_ADD):
        self.asset_ = []
        for orig_img in self.orig:
            img = orig_img.copy()
            #img.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
            img.fill(colour[0:3] + (0,), None, mode)
            img.set_colorkey(colour)
            self.asset_.append(img)

    def restore(self):
        self.asset_ = self.orig

    @property
    def asset(self):
        return self.asset_[self.curr_idx]

    def update(self, clock):
        if len(self.asset_) == 1:
            return
        if not clock.get_fps() > 0.0:
            return #don't update if we don't know how fast it's running

        self.flickertimer += 1.0 / clock.get_fps()
        if self.flickertimer >= self.flickerspeed:
            self.flickertimer = 0
            self.curr_idx = (self.curr_idx + 1) % len(self.asset_)
