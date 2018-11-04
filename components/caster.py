from components.ingredients import Ingredient
from components.spell import Spell


class Caster:
    def __init__(self, num_slots, num_spells):
        self.num_slots = num_slots
        self.num_spells = num_spells
        self.spells = [Spell.EMPTY for _ in range(num_spells)]
        self.slots = [Ingredient.FIRE for _ in range(num_slots)]

