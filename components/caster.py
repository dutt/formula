from components.ingredients import Ingredient
from components.spell import Spell


class Caster:
    def __init__(self, num_slots, num_spells):
        self.num_slots = num_slots
        self.num_spells = num_spells
        self.spells = [Spell.EMPTY for _ in range(num_spells)]
        self.slots = [Ingredient.FIRE for _ in range(num_slots)]
        self.cooldowns = {}

    def set_spells(self, spells):
        self.spells = spells
        for s in self.spells:
            s.caster = self

    def is_on_cooldown(self, spell_idx):
        if not spell_idx in self.cooldowns:
            return False
        return self.cooldowns[spell_idx] > 0

    def add_cooldown(self, spell_idx, cooldown):
        self.cooldowns[spell_idx] = cooldown

    def tick_cooldowns(self):
        to_remove = []
        for spell_idx in self.cooldowns:
            self.cooldowns[spell_idx] = self.cooldowns[spell_idx] - 1
            if self.cooldowns[spell_idx] <= 0:
                to_remove.append(spell_idx)
        for r in to_remove:
            print("Spell {} ended cooldown".format(r.text_repr))
            del self.cooldowns[r]
