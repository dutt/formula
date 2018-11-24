import tcod

from components.effects import EffectType
from messages import Message

from components.damage_type import DamageType

class Formula:
    EMPTY = None  # set in formula_builder.py

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.formula_idx = kwargs["formula_idx"]
        self.slots = kwargs["slots"]
        self.cooldown = kwargs["cooldown"]
        self.distance = float(kwargs["distance"]) + 0.5  # for diagonal
        self.area = float(kwargs["area"]) + 0.5
        self.effects = kwargs["effects"]

        self.targeting_message_text = self.text_stats_text = self.applied_text = None
        self.parse()

    def parse(self):
        text_msg = ""
        applied_msg = ""
        for e in self.effects:
            stats = e.stats
            if stats.type == EffectType.DAMAGE:
                name = stats.dmg_type.name.lower()
                text = "{} {} damage, ".format(stats.amount, name)
                text_msg += text
                applied_msg += "takes {} {} damage, ".format(stats.amount, name)
            elif stats.type == EffectType.HEALING:
                text = "{} healing, ".format(stats.amount)
                text_msg += text
                applied_msg += "healed for {}, ".format(stats.amount)
            elif stats.type == EffectType.SLOW:
                text = "slow for {} rounds, ".format(stats.rounds)
                text_msg += text
                applied_msg += "slowed for {} rounds, ".format(stats.rounds)
        postfix = "range={}, area={}".format(self.distance, self.area)
        if text_msg:
            self.targeting_message_text = "Targeting, {}, {}".format(text_msg[:-2], postfix)
            self.text_stats_text = "{}, {}".format(text_msg[:-2], postfix)
            self.applied_text = "The {} is " + applied_msg[:-2]
        else:
            self.targeting_message_text = ""
            self.text_stats_text = ""
            self.applied_text = ""


    @property
    def targeting_message(self):
        return Message(self.targeting_message_text)

    @property
    def text_repr(self):
        return "".join([s.shortname for s in self.slots])

    @property
    def text_stats(self):
        return self.text_stats_text

    def apply(self, **kwargs):
        def get_msg(e):
            return  self.applied_text.format(e.name)

        caster = kwargs.get("caster")
        target_x = kwargs.get("target_x")
        target_y = kwargs.get("target_y")
        entities = kwargs.get("entities")
        fov_map = kwargs.get("fov_map")
        results = []

        if caster.distance(target_x, target_y) > self.distance:
            results.append({"cast": False, "message": Message("Target out of range", tcod.yellow)})
            return results
        elif self.area < 1.5:  # no aoe
            for e in entities:
                if not e.fighter or not tcod.map_is_in_fov(fov_map, target_x, target_y):
                    continue
                if e.pos.x == target_x and e.pos.y == target_y:
                    results.append({"cast": True, "message": Message(get_msg(e)), "targets": [e], "formula": self})
                    for effect in self.effects:
                        results.extend(effect.apply(e))
                        if effect.stats.rounds > 1:
                            e.add_effect(effect, effect.stats.rounds)
                    break
            else:
                results.append({"cast": False, "message": Message("No target"), "targets": [], "formula": self})
        else:  # aoe formula
            targets = []
            results.append(
                    {"cast": True, "targets": targets, "formula": self, "message": Message("Splash vial thrown")})
            for e in entities:
                if not e.fighter or not tcod.map_is_in_fov(fov_map, target_x, target_y):
                    continue
                if e.distance(target_x, target_y) < self.area:
                    results.append({"message": Message(get_msg(e))})
                    for effect in self.effects:
                        results.extend(effect.apply(e))
                        if effect.stats.rounds > 1:
                            e.add_effect(effect, effect.stats.rounds)
                    targets.append(e)
        return results
