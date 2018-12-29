import pygame

from components.drawable import Drawable
from util import Vec


class VisualEffectSystem:
    _instance = None

    def __init__(self, fps_per_second):
        assert not VisualEffectSystem._instance
        VisualEffectSystem._instance = self
        self.fps_per_second = fps_per_second
        self.temporary_effects = []
        self.attached_effects = []

    @staticmethod
    def get():
        return VisualEffectSystem._instance

    @property
    def effects(self):
        return self.temporary_effects + self.attached_effects

    def update(self, game_data, gfx_data):
        for e in self.temporary_effects:
            e.update()
        for e in self.attached_effects:
            e.update()
        for e in game_data.map.entities:
            if e.drawable:
                e.drawable.update(gfx_data.clock)

    def remove(self, visual):
        if visual in self.temporary_effects:
            self.temporary_effects.remove(visual)
        elif visual in self.attached_effects:
            self.attached_effects.remove(visual)

    def add_temporary(self, pos, endpos, lifespan, asset, color=None, wait=None, transform=None):
        fps_lifespan = lifespan * self.fps_per_second
        if wait:
            fps_wait = wait * self.fps_per_second
            fps_lifespan += wait * self.fps_per_second
        else:
            fps_wait = 0
        drawable = Drawable(asset)
        effect = TemporaryVisualEffect(pos, endpos, fps_lifespan, drawable, color, owner=self, wait=fps_wait,
                                       transform=transform(fps_lifespan) if transform else None)
        self.temporary_effects.append(effect)
        return effect

    def add_attached(self, owner, asset, color=None, transform=None):
        drawable = Drawable(asset)
        effect = AttachedVisualEffect(owner, drawable, color, transform)
        self.attached_effects.append(effect)
        return effect

    @property
    def done(self):
        return len(self.temporary_effects) == 0


def fader_transform(fps_lifespan):
    def doer(drawable):
        fade_per_tick = 255 / fps_lifespan
        old_alpha = drawable.asset[0].get_alpha()
        drawable.asset[0].set_alpha(old_alpha - fade_per_tick)
        return drawable

    return doer


def rotation_transform(_=None):
    def doer(drawable):
        return Drawable([pygame.transform.rotate(drawable.asset, 90)])

    return doer


class TemporaryVisualEffect():
    def __init__(self, pos, endpos, lifespan, drawable, color, owner, wait, transform=None):
        self.pos = pos
        self.endpos = endpos
        self.lifespan = lifespan
        self.wait = wait
        self.age = 0
        if pos != endpos:
            distance = pos.distance_to(endpos)
            distance_per_update = distance / self.lifespan
            vec = endpos - pos
            normalized = vec.normalize()
            self.move_per_update = normalized * distance_per_update
        else:
            self.move_per_update = Vec(0, 0)
        self.drawable = drawable
        self.drawable.owner = self
        self.owner = owner
        self.transform = transform

        if color:
            self.drawable.colorize(color)

    @property
    def visible(self):
        return self.age >= self.wait

    def update(self):
        self.pos += self.move_per_update
        self.age += 1
        if self.transform:
            self.drawable = self.transform(self.drawable)
        if self.age > self.lifespan:
            self.owner.remove(self)


class AttachedVisualEffect():
    def __init__(self, owner, drawable, color, transform):
        self.pos = owner.pos
        self.owner = owner
        self.drawable = drawable
        if color:
            self.drawable.colorize(color)
        self.transform = transform

    @property
    def visible(self):
        return True

    def update(self):
        self.pos = self.owner.pos
        if self.transform:
            self.drawable = self.transform(self.drawable)
