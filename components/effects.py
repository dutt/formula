from enum import Enum, auto

from attrdict import AttrDict

from components.damage_type import DamageType


class EffectType(Enum):
    DAMAGE = auto()
    HEALING = auto()
    SLOW = auto()


class Effect:
    def __init__(self, rounds, applicator, stats_func, colorize_visual_func, restore_visual_func):
        self.rounds = rounds
        self.rounds_left = rounds
        self.applicator = applicator
        self.stats_func = stats_func
        self.colorize_visual = colorize_visual_func
        self.restore_visual = restore_visual_func

    def apply(self, target):
        return self.applicator(target)

    @property
    def stats(self):
        return self.stats_func()

    def tick(self):
        self.rounds_left -= 1

    @property
    def valid(self):
        return self.rounds_left > 0


class EffectBuilder:
    @staticmethod
    def create(effect_type, **kwargs):
        def create_damage(**kwargs):
            amount = kwargs["amount"]
            dmg_type = kwargs["dmg_type"]
            rounds = kwargs["rounds"]

            def apply(target):
                dmg_amount = amount
                if dmg_type in target.fighter.immunities:
                    return
                if dmg_type in target.fighter.resistances:
                    dmg_amount = amount // 2
                return target.fighter.take_damage(dmg_amount, dmg_type)

            def stats_func():
                return AttrDict({
                    "type": EffectType.DAMAGE,
                    "amount": amount,
                    "dmg_type": dmg_type,
                    "rounds": rounds
                })

            def colorize_visual(_):
                pass

            def restore_visual(_):
                pass

            return Effect(rounds, apply, stats_func, colorize_visual, restore_visual)

        def create_healing(**kwargs):
            amount = kwargs["amount"]
            rounds = kwargs["rounds"]

            def apply(target):
                heal_amount = amount
                if DamageType.LIFE in target.fighter.immunitites:
                    return
                if DamageType.LIFE in target.fighter.resistances:
                    heal_amount = amount // 2
                return target.fighter.heal(heal_amount)

            def stats_func():
                return AttrDict({
                    "type": EffectType.HEALING,
                    "amount": amount,
                    "rounds": rounds
                })

            def colorize_visual(_):
                pass

            def restore_visual(_):
                pass

            return Effect(rounds, apply, stats_func, colorize_visual, restore_visual)

        def create_slow(**kwargs):
            rounds = kwargs["rounds"]

            def apply(target):
                target.round_speed = target.round_speed // 2
                return []
                # return [{"message": Message("The {} is slowed".format(target.name))}]

            def stats_func():
                return AttrDict({
                    "type": EffectType.SLOW,
                    "rounds": rounds
                })

            def colorize_visual(target):
                target.drawable.colorize((0, 0, 255))

            def restore_visual(target):
                target.drawable.restore()

            return Effect(rounds, apply, stats_func, colorize_visual, restore_visual)

        if effect_type == EffectType.DAMAGE:
            return create_damage(**kwargs)
        elif effect_type == EffectType.HEALING:
            return create_healing(**kwargs)
        elif effect_type == EffectType.SLOW:
            return create_slow(**kwargs)
