import math

import config
from components.damage_type import DamageType
from components.effect_type import EffectType
from components.formula import Formula
from components.ingredients import Ingredient, IngredientState
from systems.effect_builder import EffectBuilder

class FormulaBuilder:
    def __init__(self, num_slots, num_formula, run_tutorial):
        self.currslot = 0
        self.currformula = 0
        self.num_slots = num_slots
        self.num_formula = num_formula
        self.run_tutorial = run_tutorial
        self.unlock_state = self.init_lock_state()
        self.set_initial_slots()

    def set_initial_slots(self):
        if self.run_tutorial or config.conf.starting_mode == "fire":
            self.slots = [
                [Ingredient.FIRE, Ingredient.FIRE, Ingredient.RANGE],
                [Ingredient.FIRE, Ingredient.RANGE, Ingredient.RANGE],
                [Ingredient.EARTH, Ingredient.EARTH, Ingredient.EARTH],
            ]
        elif config.conf.starting_mode == "choose":
            self.slots = [[Ingredient.EMPTY for i in range(self.num_slots)] for i in range(self.num_formula)]

    def init_lock_state(self):
        upgrades_unlocked = {
            # fire
            Ingredient.INFERNO: False,  # damage
            Ingredient.FIREBOLT: False,  # range
            Ingredient.FIRESPRAY: False,  # area
            # water
            Ingredient.SLEET: False,  # slow
            Ingredient.ICE: False,  # damage
            Ingredient.ICEBOLT: False,  # range
            Ingredient.ICE_VORTEX: False,  # area
            # earth
            Ingredient.ROCK: False,
            Ingredient.MAGMA: False,
            Ingredient.MUD: False,
            # life
            Ingredient.VITALITY: False,
        }
        if config.conf.unlock_mode == "none":
            basics = {
                Ingredient.EMPTY: True,
                Ingredient.FIRE: True,
                Ingredient.RANGE: True,
                Ingredient.AREA: True,
                Ingredient.WATER: True,
                Ingredient.LIFE: True,
                Ingredient.EARTH: True,
            }
        else:
            basics = {
                Ingredient.EMPTY: True,
                Ingredient.FIRE: True,
                Ingredient.RANGE: True,
                Ingredient.AREA: True,
                Ingredient.WATER: True,
                Ingredient.LIFE: True,
                Ingredient.EARTH: True,
            }
        return {**upgrades_unlocked, **basics}

    def available_upgrades(self):
        retr = []
        skip = []

        # first set up associative groups, you only get one fire upgrade etc
        for ing in Ingredient.all():
            if not self.ingredient_unlocked(ing):
                continue
            skip.extend(ing.associated)

        for ing in Ingredient.all():
            if self.ingredient_unlocked(ing):
                continue
            if ing in skip:
                continue
            if ing.is_upgraded:
                base = ing.get_base_form()
                if not self.ingredient_unlocked(base): # base has to be unlocked first
                    continue
            retr.append(ing)
        return retr

    def current_ingredient_choices(self):
        full = [Ingredient.EMPTY]
        for ing in Ingredient.all():
            if self.ingredient_unlocked(ing):
                full.append(ing)

        # now we need to remove Fire if we have Inferno etc
        skip = []
        for ing in full:
            if ing.is_upgraded:
                base = ing.get_base_form()
                skip.append(base)

        retr = [ing for ing in full if ing not in skip]
        return retr

    def ingredient_unlocked(self, ingredient):
        return self.unlock_state[ingredient]

    def unlock_ingredient(self, ingredient):
        self.unlock_state[ingredient] = True

    def replace_all(self, to_replace, replace_with):
        for formula in self.slots:
            for idx, _ in enumerate(formula):
                if formula[idx] == to_replace:
                    formula[idx] = replace_with

    def get_upgraded(self, ingredient):
        upgrades = [ing for ing in Ingredient.all() if ing.is_upgraded]
        upgrades = [ing for ing in upgrades if self.ingredient_unlocked(ing)]
        for ing in upgrades:
            if ing.get_base_form() == ingredient:
                return ing
        return ingredient

    def set_slot(self, slot, ingredient):
        self.slots[self.currformula][slot] = self.get_upgraded(ingredient)

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

    def get_empty_formula(self, caster):
        return self.evaluate_formula(
            slots=[Ingredient.EMPTY for i in range(self.num_slots)],
            formula_index=0,
            state=IngredientState(),
            caster=caster,
        )

    def evaluate_formula(self, slots, formula_index, state, caster):
        def scale_ingredient(value):
            if config.conf.ingredient_scaling:
                return max(1, math.floor(value * 0.9))
            return value

        fire_dmg = 0
        water_dmg = 0
        distance = 1
        area = 0.5
        cooldown = len([s for s in slots if s != Ingredient.EMPTY]) * state.cooldown_per_slot
        healing = 0
        slow_rounds = 0
        shield = 0
        targeted = True
        attack_modifier = False
        attack_ingredient = False
        for slot in slots:
            if slot != Ingredient.EMPTY and not slot.targeted:
                targeted = False

            if slot == Ingredient.FIRE:
                fire_dmg += state.dmg_per_step * 2
                attack_ingredient = True
            elif slot == Ingredient.RANGE:
                attack_modifier = True
                distance += state.distance_per_step * 2
            elif slot == Ingredient.AREA:
                attack_modifier = True
                area += state.area_per_step * 2
            elif slot == Ingredient.WATER:
                slow_rounds += state.slow_per_step
                attack_ingredient = True
                water_dmg += state.dmg_per_step
            elif slot == Ingredient.LIFE:
                healing += state.heal_per_step * 2
            elif slot == Ingredient.EARTH:
                shield += state.shield_per_step * 2

            # fire upgrades
            elif slot == Ingredient.INFERNO:
                fire_dmg += state.dmg_per_step * 3
                attack_ingredient = True
            elif slot == Ingredient.FIREBOLT:
                fire_dmg += state.dmg_per_step * 2
                distance += state.distance_per_step
                attack_ingredient = True
            elif slot == Ingredient.FIRESPRAY:
                fire_dmg += state.dmg_per_step * 2
                area += state.area_per_step
                attack_ingredient = True

            # water upgrades
            elif slot == Ingredient.SLEET:
                water_dmg += state.dmg_per_step
                slow_rounds += state.slow_per_step * 2
                attack_ingredient = True
            elif slot == Ingredient.ICE:
                water_dmg += state.dmg_per_step * 2
                slow_rounds += state.slow_per_step
                attack_ingredient = True
            elif slot == Ingredient.ICE_VORTEX:
                water_dmg += state.dmg_per_step
                slow_rounds += state.slow_per_step
                area += state.area_per_step
                attack_ingredient = True
            elif slot == Ingredient.ICEBOLT:
                water_dmg += state.dmg_per_step
                slow_rounds += state.slow_per_step
                distance += state.distance_per_step
                attack_ingredient = True

            # life upgrades
            elif slot == Ingredient.VITALITY:
                healing += state.heal_per_step * 3

            # earth upgrades
            elif slot == Ingredient.ROCK:
                shield += state.shield_per_step * 3
            elif slot == Ingredient.MAGMA:
                shield += state.shield_per_step
                fire_dmg += state.dmg_per_step
            elif slot == Ingredient.MUD:
                shield += state.shield_per_step
                slow_rounds += state.slow_per_step

            # scale ingredients
            if fire_dmg:
                state.dmg_per_step = scale_ingredient(state.dmg_per_step)
            if healing:
                state.heal_per_step = scale_ingredient(state.heal_per_step)
            if shield:
                state.shield_per_step = scale_ingredient(state.shield_per_step)
            # if slow
            #    state.slow_per_step = scale_ingredient(state.slow_per_step)
            # if distance:
            #    state.distance_per_step = scale_ingredient(state.distance_per_step)
            # if area:
            #    state.area_per_step = scale_ingredient(state.area_per_step)

        if attack_modifier and not attack_ingredient:
            suboptimal = "Attack modifier but no damage"
        elif healing > 0 and attack_ingredient:
            suboptimal = "Both damage and heal"
        elif area > 1 and distance < 2:
            suboptimal = "Area but no range"
        else:
            suboptimal = None
        effects = []
        if shield:
            strikebacks = []
            if fire_dmg > 0:
                strikebacks.append(
                    EffectBuilder.create(
                        EffectType.DAMAGE, caster=caster, rounds=1, amount=fire_dmg, dmg_type=DamageType.FIRE,
                    )
                )
            if water_dmg > 0:
                strikebacks.append(
                    EffectBuilder.create(
                        EffectType.DAMAGE, caster=caster, rounds=1, amount=water_dmg, dmg_type=DamageType.COLD,
                    )
                )
            if slow_rounds > 0:
                strikebacks.append(EffectBuilder.create(EffectType.SLOW, rounds=slow_rounds))

            if healing > 0:
                effects.append(EffectBuilder.create(EffectType.HEALING, rounds=1, amount=healing))
            effects.append(
                EffectBuilder.create(EffectType.DEFENSE, level=shield, strikebacks=strikebacks, distance=distance,)
            )
        else:
            if fire_dmg > 0:
                effects.append(
                    EffectBuilder.create(
                        EffectType.DAMAGE, caster=caster, rounds=1, amount=fire_dmg, dmg_type=DamageType.FIRE,
                    )
                )
            if water_dmg > 0:
                effects.append(
                    EffectBuilder.create(
                        EffectType.DAMAGE, caster=caster, rounds=1, amount=water_dmg, dmg_type=DamageType.COLD,
                    )
                )
            if slow_rounds > 0:
                effects.append(EffectBuilder.create(EffectType.SLOW, rounds=slow_rounds))
            if healing > 0:
                effects.append(EffectBuilder.create(EffectType.HEALING, rounds=1, amount=healing))

        return (
            Formula(
                slots=slots,
                cooldown=cooldown,
                formula_idx=formula_index,
                distance=distance,
                area=area,
                effects=effects,
                targeted=targeted,
                suboptimal=suboptimal,
            ),
            state,
        )

    def evaluate_entity(self, caster):
        state = IngredientState()
        retr = []
        for idx, formula in enumerate(range(self.num_formula)):
            slots = self.slots_for_formula(formula)
            formula, state = self.evaluate_formula(slots, idx, state, caster)
            retr.append(formula)
        return retr
