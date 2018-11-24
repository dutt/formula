from components.drawable import Drawable
from util import Vec


class VisualEffectSystem():
    def __init__(self, fps_per_second):
        self.fps_per_second = fps_per_second
        self.effects = []

    def update(self):
        for e in self.effects:
            e.update()

    def remove(self, visual):
        self.effects.remove(visual)

    def add(self, pos, endpos, lifespan, asset, color=None):
        fps_lifespan = lifespan * self.fps_per_second
        drawable = Drawable(asset)
        effect = VisualEffect(pos, endpos, fps_lifespan, drawable, color, owner=self)
        self.effects.append(effect)

    @property
    def done(self):
        return len(self.effects) == 0

class VisualEffect():
    def __init__(self, pos, endpos, lifespan, drawable, color, owner):
        self.pos = pos
        self.endpos = endpos
        self.lifespan = lifespan
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
        if color:
            self.drawable.colorize(color)

    def update(self):
        self.pos += self.move_per_update
        self.age += 1
        if self.age > self.lifespan:
            self.owner.remove(self)
