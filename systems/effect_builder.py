from attrdict import AttrDict

from components.effects import Effect
from components.damage_type import DamageType
from components.effect_type import EffectType
from components.shield import Shield
from graphics.assets import Assets
from graphics.visual_effect import VisualEffectSystem, rotation_transform

class EffectBuilder:
    @staticmethod
    def create(effect_type, **kwargs):
        def create_damage(**kwargs):
            amount = kwargs["amount"]
            dmg_type = kwargs["dmg_type"]
            rounds = kwargs["rounds"]
            caster = kwargs["caster"]
            assert amount
            assert dmg_type
            assert rounds
            assert caster

            def apply(target):
                dmg_amount = amount
                color = None
                base = 100
                main = 200
                if dmg_type == DamageType.FIRE:
                    color = (main, base, base)
                elif dmg_type == DamageType.COLD:
                    color = (base, base, main)
                VisualEffectSystem.get().add_temporary(
                    target.pos, target.pos, lifespan=0.2, asset=Assets.get().spark_effect, color=color, wait=0.2,
                )
                return target.fighter.take_damage(source=caster, dmg=dmg_amount, dmg_type=dmg_type)

            def stats_func():
                return AttrDict({"type": EffectType.DAMAGE, "amount": amount, "dmg_type": dmg_type, "rounds": rounds})

            return Effect(rounds, apply, stats_func)

        def create_healing(**kwargs):
            amount = kwargs["amount"]
            rounds = kwargs["rounds"]
            assert amount
            assert rounds

            def apply(target):
                heal_amount = amount
                if DamageType.LIFE in target.fighter.immunities:
                    return
                if DamageType.LIFE in target.fighter.resistances:
                    heal_amount = amount // 2
                return target.fighter.heal(heal_amount)

            def stats_func():
                return AttrDict({"type": EffectType.HEALING, "amount": amount, "rounds": rounds})

            return Effect(rounds, apply, stats_func)

        def create_slow(**kwargs):
            rounds = kwargs["rounds"]
            assert rounds

            def apply(target):
                #target.round_speed = target.round_speed // 5
                target.round_speed = 0
                return []

            def stats_func():
                return AttrDict({"type": EffectType.SLOW, "rounds": rounds})

            def colorize_visual(target):
                target.drawable.colorize((0, 0, 255))

            return Effect(rounds, apply, stats_func, colorize_visual)

        def create_defense(**kwargs):
            level = kwargs["level"]
            strikebacks = kwargs["strikebacks"]
            distance = kwargs["distance"]
            assert level
            assert strikebacks is not None
            assert distance is not None

            def apply(target):
                target.fighter.shield = Shield(level, strikebacks, target, distance)
                target.fighter.shield.visual_effect = VisualEffectSystem.get().add_attached(
                    target, Assets.get().shield_effect, target.fighter.shield.color, transform=rotation_transform(),
                )
                return []

            def stats_func():
                return AttrDict({"type": EffectType.DEFENSE, "rounds": 1, "level": level, "strikebacks": strikebacks,})

            def colorize_visual(target):
                target.drawable.colorize((0, 0, 255))

            return Effect(rounds=None, applicator=apply, stats_func=stats_func, colorize_visual_func=colorize_visual,)

        if effect_type == EffectType.DAMAGE:
            return create_damage(**kwargs)
        elif effect_type == EffectType.HEALING:
            return create_healing(**kwargs)
        elif effect_type == EffectType.SLOW:
            return create_slow(**kwargs)
        elif effect_type == EffectType.DEFENSE:
            return create_defense(**kwargs)
