from enum import Enum, auto


class Ingredient(Enum):
    EMPTY = auto()
    FIRE = auto()
    RANGE = auto()
    AREA = auto()
    COLD = auto()
    LIFE = auto()
    SHIELD = auto()

    # leveled up fire
    INFERNO = auto()
    FIRESPRAY = auto()
    FIREBOLT = auto()

    @property
    def shortname(self):
        return self.name[0:1].capitalize()

    @property
    def description(self):
        if self == Ingredient.FIRE:
            return "Fire ingredient, increase formula damage"
        elif self == Ingredient.RANGE:
            return "Range ingredient, increase formula range"
        elif self == Ingredient.AREA:
            return "Area ingredient, increase area of the formula"
        elif self == Ingredient.COLD:
            return "Cold ingredient, add minor damage and slow down targets"
        elif self == Ingredient.LIFE:
            return "Life ingredient, heals the target HP"
        elif self == Ingredient.SHIELD:
            return "Shield ingredient, add shield points, makes the formula defensive"
        elif self == Ingredient.INFERNO:
            return "Level up Fire to Inferno, twice the damage"
        elif self == Ingredient.FIREBOLT:
            return "Level up Fire to Firebolt, damage and range in one"
        elif self == Ingredient.FIRESPRAY:
            return "Level up Fire to Firespray, damage and area in one"
        else:
            return str(self)

    @property
    def targeted(self):
        return self in [Ingredient.FIRE,
                        Ingredient.RANGE,
                        Ingredient.AREA,
                        Ingredient.COLD,

                        Ingredient.INFERNO,
                        Ingredient.FIREBOLT,
                        Ingredient.FIRESPRAY]
