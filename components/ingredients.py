from enum import Enum, auto


class Ingredient(Enum):
    EMPTY = auto()
    FIRE = auto()
    RANGE = auto()
    AREA = auto()
    WATER = auto()
    LIFE = auto()
    EARTH = auto()

    # leveled up fire
    INFERNO = auto()
    FIRESPRAY = auto()
    FIREBOLT = auto()

    # leveled up cold
    SLEET = auto()
    ICE = auto()
    ICEBOLT = auto()
    ICE_VORTEX = auto()

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
        elif self == Ingredient.WATER:
            return "Water ingredient, add minor damage and slow down targets"
        elif self == Ingredient.LIFE:
            return "Life ingredient, heals the target HP"
        elif self == Ingredient.EARTH:
            return "Earth ingredient, add shield points, makes the formula defensive"
        elif self == Ingredient.INFERNO:
            return "Level up Fire to Inferno, twice the damage"
        elif self == Ingredient.FIREBOLT:
            return "Level up Fire to Firebolt, damage and range in one"
        elif self == Ingredient.FIRESPRAY:
            return "Level up Fire to Firespray, damage and area in one"
        elif self == Ingredient.SLEET:
            return "Level up Ice to Sleet, slow for twice as long"
        elif self == Ingredient.ICE:
            return "Level up Water to Ice, double damage"
        elif self == Ingredient.ICEBOLT:
            return "Level up water to IceBolt, add range"
        elif self == Ingredient.ICE_VORTEX:
            return "Level up Water to Ice vortex, add area effect"
        else:
            return str(self)

    @property
    def targeted(self):
        return self in [
            Ingredient.FIRE,
            Ingredient.RANGE,
            Ingredient.AREA,
            Ingredient.WATER,
            Ingredient.INFERNO,
            Ingredient.FIREBOLT,
            Ingredient.FIRESPRAY,
            Ingredient.SLEET,
            Ingredient.ICE,
            Ingredient.ICE_VORTEX,
            Ingredient.ICEBOLT,
        ]
