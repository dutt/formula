import math

import config
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
        self.unlock_state = self.init_lock_state()
        if config.conf.starting_mode == "choose":
            self.slots = [
                [Ingredient.EMPTY for i in range(num_slots)] for i in range(num_formula)
            ]
        elif config.conf.starting_mode == "fire":
            self.slots = [
                [Ingredient.FIRE, Ingredient.FIRE, Ingredient.RANGE],
                [Ingredient.FIRE, Ingredient.RANGE, Ingredient.RANGE],
                [Ingredient.FIRE, Ingredient.RANGE, Ingredient.RANGE],
            ]

    def init_lock_state(self):
        upgrades_unlocked = {
            # fire
            Ingredient.INFERNO: False, # damage
            Ingredient.FIREBOLT: False, # range
            Ingredient.FIRESPRAY: False, # area
            # water
            Ingredient.SLEET: False, # slow
            Ingredient.ICE: False, # damage
            Ingredient.ICEBOLT: False, # range
            Ingredient.ICE_VORTEX: False, # area
            # earth
            Ingredient.ROCK : False,
            Ingredient.MAGMA : False,
            Ingredient.MUD : False,
            # life
            Ingredient.VITALITY : False
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
                Ingredient.AREA: False,
                Ingredient.WATER: True,
                Ingredient.LIFE: True,
                Ingredient.EARTH: True,
            }
        return {**upgrades_unlocked, **basics}

    def ingredient_unlocked(self, ingredient):
        return self.unlock_state[ingredient]

    def unlock_ingredient(self, ingredient):
        self.unlock_state[ingredient] = True

    def replace_all(self, to_replace, replace_with):
        for formula in self.slots:
            for idx, slot in enumerate(formula):
                if formula[idx] == to_replace:
                    formula[idx] = replace_with

    def get_upgraded(self, ingredient):
        if ingredient == Ingredient.FIRE:
            if self.ingredient_unlocked(Ingredient.INFERNO):
                return Ingredient.INFERNO
            elif self.ingredient_unlocked(Ingredient.FIREBOLT):
                return Ingredient.FIREBOLT
            elif self.ingredient_unlocked(Ingredient.FIRESPRAY):
                return Ingredient.FIRESPRAY

        elif ingredient == Ingredient.WATER:
            if self.ingredient_unlocked(Ingredient.SLEET):
                return Ingredient.SLEET
            elif self.ingredient_unlocked(Ingredient.ICE):
                return Ingredient.ICE
            elif self.ingredient_unlocked(Ingredient.ICEBOLT):
                return Ingredient.ICEBOLT
            elif self.ingredient_unlocked(Ingredient.ICE_VORTEX):
                return Ingredient.ICE_VORTEX

        elif ingredient == Ingredient.LIFE:
            if self.ingredient_unlocked(Ingredient.VITALITY):
                return Ingredient.VITALITY

        elif ingredient == Ingredient.EARTH:
            if self.ingredient_unlocked(Ingredient.ROCK):
                return Ingredient.ROCK
            elif self.ingredient_unlocked(Ingredient.MAGMA):
                return Ingredient.MAGMA
            elif self.ingredient_unlocked(Ingredient.MUD):
                return Ingredient.MUD

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

    def evaluate(self, caster):
        def scale_ingredient(value):
            if config.conf.ingredient_scaling:
                return max(1, math.floor(value * 0.9))
            return value

        retr = []
        fire_dmg_per_step = 10
        water_dmg_per_step = 5
        distance_per_step = 2
        area_per_step = 0.5
        cooldown_per_slot = 3
        slow_per_step = 3
        heal_per_step = 3
        shield_per_step = 4
        for idx, formula in enumerate(range(self.num_formula)):
            slots = self.slots_for_formula(formula)
            fire_dmg = 0
            water_dmg = 0
            distance = 1
            area = 0.5
            cooldown = len(slots) * cooldown_per_slot
            healing = 0
            slow_rounds = 0
            shield = 0
            targeted = True
            attack_modifier = False
            attack_ingredient = False
            for slot in slots:
                if slot != Ingredient.EMPTY and not slot.targeted:
                    targeted = False
                if slot == Ingredient.EMPTY:
                    cooldown -= cooldown_per_slot
                elif slot == Ingredient.FIRE:
                    fire_dmg += fire_dmg_per_step
                    attack_ingredient = True
                elif slot == Ingredient.RANGE:
                    attack_modifier = True
                    distance += distance_per_step
                elif slot == Ingredient.AREA:
                    attack_modifier = True
                    area += area_per_step
                elif slot == Ingredient.WATER:
                    slow_rounds += slow_per_step
                    attack_ingredient = True
                    water_dmg += water_dmg_per_step
                elif slot == Ingredient.LIFE:
                    healing += heal_per_step
                elif slot == Ingredient.EARTH:
                    shield += shield_per_step

                # fire upgrades
                elif slot == Ingredient.INFERNO:
                    fire_dmg += 2 * fire_dmg_per_step
                    attack_ingredient = True
                elif slot == Ingredient.FIREBOLT:
                    fire_dmg += fire_dmg_per_step
                    distance += distance_per_step
                    attack_ingredient = True
                elif slot == Ingredient.FIRESPRAY:
                    fire_dmg += fire_dmg_per_step
                    area += area_per_step
                    attack_ingredient = True

                # water upgrades
                elif slot == Ingredient.SLEET:
                    water_dmg += water_dmg_per_step
                    slow_rounds += slow_per_step * 2
                    attack_ingredient = True
                elif slot == Ingredient.ICE:
                    water_dmg += water_dmg_per_step * 2
                    slow_rounds += slow_per_step
                    attack_ingredient = True
                elif slot == Ingredient.ICE_VORTEX:
                    water_dmg += water_dmg_per_step
                    slow_rounds += slow_per_step
                    area += area_per_step
                    attack_ingredient = True
                elif slot == Ingredient.ICEBOLT:
                    water_dmg += water_dmg_per_step
                    slow_rounds += slow_per_step
                    distance += distance_per_step
                    attack_ingredient = True

                # life upgrades
                elif slot == Ingredient.VITALITY:
                    healing += 2 * heal_per_step

                # earth upgrades
                elif slot == Ingredient.ROCK:
                    shield += 2 * shield_per_step
                elif slot == Ingredient.MAGMA:
                    shield += shield_per_step
                    fire_dmg += math.ceil(fire_dmg_per_step * 0.5)
                elif slot == Ingredient.MUD:
                    shield += shield_per_step
                    fire_dmg += math.ceil(fire_dmg_per_step * 0.5)

                # scale ingredients
                if fire_dmg:
                    fire_dmg_per_step = scale_ingredient(fire_dmg_per_step)
                if water_dmg:
                    water_dmg_per_step = scale_ingredient(water_dmg_per_step)
                if healing:
                    heal_per_step = scale_ingredient(heal_per_step)
                if shield:
                    shield_per_step = scale_ingredient(shield_per_step)
                if distance:
                    distance_per_step = scale_ingredient(distance_per_step)
                if area:
                    area_per_step = scale_ingredient(area_per_step)

            if attack_modifier and not attack_ingredient:
                suboptimal = True
            elif healing > 0 and attack_ingredient:
                suboptimal = True
            else:
                suboptimal = False
            effects = []
            if shield:
                strikebacks = []
                if fire_dmg > 0:
                    strikebacks.append(
                        EffectBuilder.create(
                            EffectType.DAMAGE,
                            caster=caster,
                            rounds=1,
                            amount=fire_dmg,
                            dmg_type=DamageType.FIRE,
                        )
                    )
                if water_dmg > 0:
                    strikebacks.append(
                        EffectBuilder.create(
                            EffectType.DAMAGE,
                            caster=caster,
                            rounds=1,
                            amount=water_dmg,
                            dmg_type=DamageType.COLD,
                        )
                    )
                if slow_rounds > 0:
                    strikebacks.append(
                        EffectBuilder.create(EffectType.SLOW, rounds=slow_rounds)
                    )
                effects.append(
                    EffectBuilder.create(
                        EffectType.DEFENSE,
                        level=shield,
                        strikebacks=strikebacks,
                        distance=distance,
                    )
                )
            else:
                if fire_dmg > 0:
                    effects.append(
                        EffectBuilder.create(
                            EffectType.DAMAGE,
                            caster=caster,
                            rounds=1,
                            amount=fire_dmg,
                            dmg_type=DamageType.FIRE,
                        )
                    )
                if water_dmg > 0:
                    effects.append(
                        EffectBuilder.create(
                            EffectType.DAMAGE,
                            caster=caster,
                            rounds=1,
                            amount=water_dmg,
                            dmg_type=DamageType.COLD,
                        )
                    )
                if slow_rounds > 0:
                    effects.append(
                        EffectBuilder.create(EffectType.SLOW, rounds=slow_rounds)
                    )
                if healing > 0:
                    effects.append(
                        EffectBuilder.create(
                            EffectType.HEALING, rounds=1, amount=healing
                        )
                    )

            retr.append(
                Formula(
                    slots=slots,
                    cooldown=cooldown,
                    formula_idx=idx,
                    distance=distance,
                    area=area,
                    effects=effects,
                    targeted=targeted,
                    suboptimal=suboptimal,
                )
            )
        return retr
