from enum import Enum, auto


class Ingredient(Enum):
    EMPTY = auto()
    FIRE = auto()
    RANGE = auto()
    AREA = auto()
    # COLD = auto()
    LIFE = auto()
    # SHIELD = auto()

    @property
    def shortname(self):
        return self.name[0:1].capitalize()
