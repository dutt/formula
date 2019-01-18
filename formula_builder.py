from components.damage_type import DamageType
from components.effects import EffectType, EffectBuilder
from components.formula import Formula
from components.ingredients import Ingredient


class FormulaBuilder:
    def __init__(self, num_slots, num_formula):
        self.currslot = 0
        self.currformula = 0
        self.num_slots = num_slots
        self.num_formula = num_formula
        self.slots = [[Ingredient.EMPTY for i in range(num_slots)] for i in range(num_formula)]
        self.unlock_state = self.init_lock_state()

    def init_lock_state(self):
        import config
        if config.conf.unlock_mode == "none":
            return {
                Ingredient.EMPTY: True,
                Ingredient.FIRE: True,
                Ingredient.RANGE: True,
                Ingredient.AREA: True,
                Ingredient.COLD: True,
                Ingredient.LIFE: True,
                Ingredient.SHIELD: True
            }
        else:
            return {
                Ingredient.EMPTY: True,
                Ingredient.FIRE: True,
                Ingredient.RANGE: True,
                Ingredient.AREA: False,
                Ingredient.COLD: False,
                Ingredient.LIFE: False,
                Ingredient.SHIELD: False
            }

    def ingredient_unlocked(self, ingredient):
        return self.unlock_state[ingredient]

    def unlock_ingredient(self, ingredient):
        self.unlock_state[ingredient] = True

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
        fire_dmg_per_step = 10
        cold_dmg_per_step = 5
        distance_per_step = 3
        area_per_step = 0.5
        cooldown_per_slot = 3
        slow_per_step = 2
        heal_per_step = 3
        shield_per_step = 4
        for idx, formula in enumerate(range(self.num_formula)):
            slots = self.slots_for_formula(formula)
            fire_dmg = 0
            cold_dmg = 0
            distance = 1
            area = 0.5
            cooldown = len(slots) * cooldown_per_slot
            healing = 0
            slow_rounds = 0
            shield = 0
            for slot in slots:
                if slot == Ingredient.EMPTY:
                    cooldown -= cooldown_per_slot
                elif slot == Ingredient.FIRE:
                    fire_dmg += fire_dmg_per_step
                elif slot == Ingredient.RANGE:
                    distance += distance_per_step
                elif slot == Ingredient.AREA:
                    area += area_per_step
                elif slot == Ingredient.COLD:
                    slow_rounds += slow_per_step
                    cold_dmg += cold_dmg_per_step // 2
                elif slot == Ingredient.LIFE:
                    healing += heal_per_step
                elif slot == Ingredient.SHIELD:
                    shield += shield_per_step
            effects = []
            if shield:
                strikebacks = []
                if fire_dmg > 0:
                    strikebacks.append(
                        EffectBuilder.create(EffectType.DAMAGE, rounds=1, amount=fire_dmg, dmg_type=DamageType.FIRE))
                if cold_dmg > 0:
                    strikebacks.append(
                        EffectBuilder.create(EffectType.DAMAGE, rounds=1, amount=cold_dmg, dmg_type=DamageType.COLD))
                if slow_rounds > 0:
                    strikebacks.append(EffectBuilder.create(EffectType.SLOW, rounds=slow_rounds))
                effects.append(
                    EffectBuilder.create(EffectType.DEFENSE, level=shield, strikebacks=strikebacks, distance=distance))
            else:
                if fire_dmg > 0:
                    effects.append(
                        EffectBuilder.create(EffectType.DAMAGE, rounds=1, amount=fire_dmg, dmg_type=DamageType.FIRE))
                if cold_dmg > 0:
                    effects.append(
                        EffectBuilder.create(EffectType.DAMAGE, rounds=1, amount=cold_dmg, dmg_type=DamageType.COLD))
                if slow_rounds > 0:
                    effects.append(EffectBuilder.create(EffectType.SLOW, rounds=slow_rounds))
                if healing > 0:
                    effects.append(EffectBuilder.create(EffectType.HEALING, rounds=1, amount=healing))

            retr.append(Formula(slots=slots, cooldown=cooldown, formula_idx=idx,
                                distance=distance, area=area, effects=effects))
        return retr


builder = FormulaBuilder(num_slots=3, num_formula=3)
# builder.slots = [[Ingredient.EMPTY for i in range(3)]]
builder.slots = [[Ingredient.FIRE for i in range(3)] for i in range(3)]
builder.slots = [[Ingredient.FIRE, Ingredient.RANGE, Ingredient.RANGE] for i in range(3)]
Formula.EMPTY = builder.evaluate()[0]
Formula.DEFAULT = builder.evaluate()
