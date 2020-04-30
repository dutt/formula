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

    # level up life
    VITALITY = auto()

    # leveled up earth
    ROCK = auto()
    MAGMA = auto()
    MUD = auto()

    @property
    def shortname(self):
        if self == Ingredient.EMPTY:
            return "-"
        else:
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
            return "Level up Water to Sleet, slow for twice as long"
        elif self == Ingredient.ICE:
            return "Level up Water to Ice, double damage"
        elif self == Ingredient.ICEBOLT:
            return "Level up Water to IceBolt, add range"
        elif self == Ingredient.ICE_VORTEX:
            return "Level up Water to Ice vortex, add area effect"

        elif self == Ingredient.VITALITY:
            return "Level up Life to Vitality, double the healing"

        elif self == Ingredient.ROCK:
            return "Level up Earth to Rock, double the protection"
        elif self == Ingredient.MAGMA:
            return "Level up Earth to Magma, add fire damage"
        elif self == Ingredient.MUD:
            return "Level up Earth to Mud, add slow"
        else:
            return str(self)

    @staticmethod
    def all():
        return [
            Ingredient.FIRE,
            Ingredient.RANGE,
            Ingredient.AREA,
            Ingredient.WATER,
            Ingredient.LIFE,
            Ingredient.EARTH,

            Ingredient.INFERNO,
            Ingredient.FIRESPRAY,
            Ingredient.FIREBOLT,

            Ingredient.SLEET,
            Ingredient.ICE,
            Ingredient.ICEBOLT,
            Ingredient.ICE_VORTEX,

            Ingredient.VITALITY,

            Ingredient.ROCK,
            Ingredient.MAGMA,
            Ingredient.MUD
        ]

    @staticmethod
    def upgrades():
        return [
            Ingredient.INFERNO,
            Ingredient.FIRESPRAY,
            Ingredient.FIREBOLT,

            Ingredient.SLEET,
            Ingredient.ICE,
            Ingredient.ICEBOLT,
            Ingredient.ICE_VORTEX,

            Ingredient.VITALITY,

            Ingredient.ROCK,
            Ingredient.MAGMA,
            Ingredient.MUD
        ]

    @staticmethod
    def basics():
        return [
            Ingredient.FIRE,
            Ingredient.RANGE,
            Ingredient.AREA,
            Ingredient.WATER,
            Ingredient.LIFE,
            Ingredient.EARTH
        ]

    def get_base_form(self):
        if self in IngredientMeta.UPGRADE_TO_BASE_MAP:
            return IngredientMeta.UPGRADE_TO_BASE_MAP[self]
        else:
            return self

    @property
    def is_upgraded(self):
        return self in IngredientMeta.UPGRADE_TO_BASE_MAP

    @property
    def associated(self):
        for group in IngredientMeta.UPGRADE_GROUPS:
            if self in group:
                return group
        return []

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
            Ingredient.ICEBOLT,
            Ingredient.ICE_VORTEX,
        ]

class IngredientState:
    def __init__(self):
        self.dmg_per_step = 4
        self.distance_per_step = 2
        self.area_per_step = 1
        self.cooldown_per_slot = 2
        self.slow_per_step = 5
        self.heal_per_step = 2
        self.shield_per_step = 2


class IngredientMeta():
    UPGRADE_TO_BASE_MAP = {
        Ingredient.INFERNO : Ingredient.FIRE,
        Ingredient.FIRESPRAY : Ingredient.FIRE,
        Ingredient.FIREBOLT : Ingredient.FIRE,

        Ingredient.SLEET : Ingredient.WATER,
        Ingredient.ICE : Ingredient.WATER,
        Ingredient.ICEBOLT : Ingredient.WATER,
        Ingredient.ICE_VORTEX : Ingredient.WATER,

        Ingredient.VITALITY : Ingredient.LIFE,

        Ingredient.ROCK : Ingredient.EARTH,
        Ingredient.MAGMA : Ingredient.EARTH,
        Ingredient.MUD : Ingredient.EARTH
    }

    UPGRADE_GROUPS = [
        [ Ingredient.INFERNO, Ingredient.FIRESPRAY, Ingredient.FIREBOLT ],
        [ Ingredient.SLEET,  Ingredient.ICE,  Ingredient.ICEBOLT,  Ingredient.ICE_VORTEX ],
        [ Ingredient.VITALITY ],
        [ Ingredient.ROCK, Ingredient.MAGMA, Ingredient.MUD ]
    ]
