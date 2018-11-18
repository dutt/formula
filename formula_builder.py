from components.effects import Effect, EffectTag
from components.ingredients import Ingredient
from components.formula import Formula


class FormulaBuilder:
    def __init__(self, num_slots, num_formula):
        self.currslot = 0
        self.currformula = 0
        self.num_slots = num_slots
        self.num_formula = num_formula
        self.slots = [[Ingredient.EMPTY for i in range(num_slots)] for i in range(num_formula)]

    def set_slot(self, slot, ingredient):
        self.slots[self.currformula][slot] = ingredient

    def add_slot(self):
        self.num_slots += 1
        for s in range(self.num_formula):
            self.slots[s].append(Ingredient.EMPTY)

    def add_formula(self):
        self.num_formula += 1
        self.slots.append([Ingredient.EMPTY for i in range(self.num_slots)])

    @property
    def current_slots(self):
        return self.slots[self.currformula]

    def slots_for_formula(self, formula_index):
        return self.slots[formula_index]

    def evaluate(self):
        retr = []
        dmg_per_step = 10
        distance_per_step = 3
        area_per_step = 0.5
        cooldown_per_slot = 3
        slow_per_step = 2
        heal_per_step = 3
        for idx, formula in enumerate(range(self.num_formula)):
            slots = self.slots_for_formula(formula)
            dmg = 5
            distance = 1
            area = 0.5
            cooldown = len(slots) * cooldown_per_slot
            healing = 0
            slow_rounds = 0
            for slot in slots:
                if slot == Ingredient.EMPTY:
                    cooldown -= cooldown_per_slot
                elif slot == Ingredient.FIRE:
                    dmg += dmg_per_step
                elif slot == Ingredient.RANGE:
                    distance += distance_per_step
                elif slot == Ingredient.AREA:
                    area += area_per_step
                #elif slot == Ingredient.COLD:
                #    slow_rounds += slow_per_step
                #    dmg += dmg_per_step // 2
                elif slot == Ingredient.LIFE:
                    healing += heal_per_step
            effects = []
            if dmg > 0:
                effects.append(Effect(1, EffectTag.HP_DIFF, lambda: dmg))
            if slow_rounds > 0:
                effects.append(Effect(slow_rounds, {"speed": lambda e: 0}))
            if healing > 0:
                effects.append(Effect(1, EffectTag.HP_DIFF, lambda: -healing))
            retr.append(Formula(slots=slots, cooldown=cooldown, formula_idx=idx,
                                distance=distance, area=area, effects=effects))
        return retr


builder = FormulaBuilder(num_slots=3, num_formula=3)
# builder.slots = [[Ingredient.EMPTY for i in range(3)]]
builder.slots = [[Ingredient.FIRE for i in range(3)] for i in range(3)]
# builder.slots = [[Ingredient.FIRE, Ingredient.RANGE, Ingredient.AREA]]
Formula.EMPTY = builder.evaluate()[0]
Formula.DEFAULT = builder.evaluate()
