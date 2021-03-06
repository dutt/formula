from enum import Enum, auto

import config
from graphics.constants import colors


class Ingredient(Enum):
    EMPTY = auto()
    FIRE = auto()
    WATER = auto()
    LIFE = auto()
    EARTH = auto()

    # modifiers
    AREA = auto()
    RANGE = auto()
    TRAP = auto()

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
        elif self == Ingredient.WATER:
            return "Water ingredient, add minor damage and slow down targets"
        elif self == Ingredient.LIFE:
            return "Life ingredient, heals the target HP"
        elif self == Ingredient.EARTH:
            return "Earth ingredient, add shield points, makes the formula defensive"

        elif self == Ingredient.RANGE:
            return "Range ingredient, increase formula range"
        elif self == Ingredient.AREA:
            return "Area ingredient, increase area of the formula"
        elif self == Ingredient.TRAP:
            return "Trap ingredient, turns the formula into a trap"

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
        retr = [
            Ingredient.FIRE,
            Ingredient.WATER,
            Ingredient.EARTH,
            Ingredient.RANGE,
            Ingredient.AREA,
            Ingredient.INFERNO,
            Ingredient.FIRESPRAY,
            Ingredient.FIREBOLT,
            Ingredient.SLEET,
            Ingredient.ICE,
            Ingredient.ICEBOLT,
            Ingredient.ICE_VORTEX,
            Ingredient.ROCK,
            Ingredient.MAGMA,
            Ingredient.MUD,
        ]
        if config.conf.trap:
            retr.append(Ingredient.TRAP)
        if config.conf.heal:
            retr.extend([Ingredient.LIFE, Ingredient.VITALITY])
        return retr

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
            Ingredient.MUD,
        ]

    @staticmethod
    def basics():
        retr = [
            Ingredient.FIRE,
            Ingredient.WATER,
            Ingredient.EARTH,
            Ingredient.RANGE,
            Ingredient.AREA,
        ]
        if config.conf.heal:
            retr.append(Ingredient.LIFE)
        return retr

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
            Ingredient.WATER,
            Ingredient.TRAP,
            Ingredient.RANGE,
            Ingredient.AREA,
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

class IngredientSerialization:

    @staticmethod
    def deserialize(value):
        if value == "EMPTY":
            return Ingredient.EMPTY
        elif value == "FIRE":
            return Ingredient.FIRE
        elif value == "WATER":
            return Ingredient.WATER
        elif value == "LIFE":
            return Ingredient.LIFE
        elif value == "EARTH":
            return Ingredient.EARTH

        # modifiers
        elif value == "AREA":
            return Ingredient.AREA
        elif value == "RANGE":
            return Ingredient.RANGE
        elif value == "TRAP":
            return Ingredient.TRAP

        # leveled up fire
        elif value == "INFERNO":
            return Ingredient.INFERNO
        elif value == "FIRESPRAY":
            return Ingredient.FIRESPRAY
        elif value == "FIREBOLT":
            return Ingredient.FIREBOLT

        # leveled up cold
        elif value == "SLEET":
            return Ingredient.SLEET
        elif value == "ICE":
            return Ingredient.ICE
        elif value == "ICEBOLT":
            return Ingredient.ICEBOLT
        elif value == "ICE_VORTEX":
            return Ingredient.ICE_VORTEX

        # level up life
        elif value == "VITALITY":
            return Ingredient.VITALITY

        # leveled up earth
        elif value == "ROCK":
            return Ingredient.ROCK
        elif value == "MAGMA":
            return Ingredient.MAGMA
        elif value == "MUD":
            return Ingredient.MUD

        raise ValueError(f"Can't parse ingredient '{value}'")

class IngredientMeta:
    def setup_upgrade_to_base_map():
        retr = {
            Ingredient.INFERNO: Ingredient.FIRE,
            Ingredient.FIRESPRAY: Ingredient.FIRE,
            Ingredient.FIREBOLT: Ingredient.FIRE,
            Ingredient.SLEET: Ingredient.WATER,
            Ingredient.ICE: Ingredient.WATER,
            Ingredient.ICEBOLT: Ingredient.WATER,
            Ingredient.ICE_VORTEX: Ingredient.WATER,
            Ingredient.ROCK: Ingredient.EARTH,
            Ingredient.MAGMA: Ingredient.EARTH,
            Ingredient.MUD: Ingredient.EARTH,
        }
        if config.conf.heal:
            retr[Ingredient.VITALITY] = Ingredient.LIFE
        return retr

    UPGRADE_TO_BASE_MAP = setup_upgrade_to_base_map()

    def setup_upgrade_groups():
        retr = [
            [Ingredient.INFERNO, Ingredient.FIRESPRAY, Ingredient.FIREBOLT],
            [Ingredient.SLEET, Ingredient.ICE, Ingredient.ICEBOLT, Ingredient.ICE_VORTEX],
            [Ingredient.ROCK, Ingredient.MAGMA, Ingredient.MUD],
        ]
        if config.conf.heal:
            retr.append([Ingredient.VITALITY])
        return retr

    UPGRADE_GROUPS = setup_upgrade_groups()

    INGREDIENT_COLORS = {
        Ingredient.EMPTY: colors.WHITE,
        Ingredient.FIRE: colors.RED,
        Ingredient.WATER: colors.BLUE,
        Ingredient.LIFE: colors.YELLOW,
        Ingredient.EARTH: colors.GREY,
        Ingredient.AREA: colors.BROWN,
        Ingredient.RANGE: colors.BROWN,
        Ingredient.TRAP: colors.BROWN,
        Ingredient.INFERNO: colors.RED,
        Ingredient.FIRESPRAY: colors.RED,
        Ingredient.FIREBOLT: colors.RED,
        Ingredient.SLEET: colors.BLUE,
        Ingredient.ICE: colors.BLUE,
        Ingredient.ICEBOLT: colors.BLUE,
        Ingredient.ICE_VORTEX: colors.BLUE,
        Ingredient.VITALITY: colors.YELLOW,
        Ingredient.ROCK: colors.GREY,
        Ingredient.MAGMA: colors.GREY,
        Ingredient.MUD: colors.GREY,
    }
