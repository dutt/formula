from systems.messages import Message
from components.ingredients import Ingredient
from components.formula import Formula


class Caster:
    def __init__(self, num_slots, num_formulas):
        self.num_slots = num_slots
        self.num_formulas = num_formulas
        self.formulas = None
        self.slots = [Ingredient.FIRE for _ in range(num_slots)]
        self.cooldowns = {}

    def set_formulas(self, formulas):
        self.formulas = formulas
        for s in self.formulas:
            s.caster = self

    def is_on_cooldown(self, formula_idx):
        if formula_idx not in self.cooldowns:
            return False
        return self.cooldowns[formula_idx] > 0

    def add_cooldown(self, formula_idx, cooldown):
        self.cooldowns[formula_idx] = cooldown

    def get_cooldown(self, formula_idx):
        return self.cooldowns[formula_idx]

    def tick_cooldowns(self):
        to_remove = []
        for formula_idx in self.cooldowns:
            self.cooldowns[formula_idx] = self.cooldowns[formula_idx] - 1
            if self.cooldowns[formula_idx] <= 0:
                to_remove.append(formula_idx)
        for r in to_remove:
            del self.cooldowns[r]

    cooldown_message = Message("That formula is on cooldown")
