from components.entity import Entity
from graphics.render_order import RenderOrder


class Monster(Entity):
    def __init__(self, x, y, name, speed, fighter, ai, drawable, range=None):
        super(Monster, self).__init__(
            x, y, name, speed, blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter, ai=ai, drawable=drawable,
        )
        self.range = range if range else 1.5
