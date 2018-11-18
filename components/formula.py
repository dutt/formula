import tcod

from components.effects import EffectTag
from messages import Message


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
        self.hp_total_diff = 0
        self.parse()

    def parse(self):
        for e in self.effects:
            if e.tag == EffectTag.HP_DIFF:
                self.hp_total_diff += e.apply()

    @property
    def targeting_message(self):
        if self.hp_total_diff < 0:
            msg = "Targeting, healing={}, range={}, area={}".format(self.hp_total_diff, self.distance, self.area)
        else:
            msg = "Targeting, damage={}, range={}, area={}".format(self.hp_total_diff, self.distance, self.area)
        return Message(msg)

    @property
    def text_repr(self):
        return "".join([s.shortname for s in self.slots])

    @property
    def text_stats(self):
        if self.hp_total_diff < 0:
            return "healing={}, range={}, area={}".format(self.hp_total_diff, self.distance, self.area)
        else:
            return "damage={}, range={}, area={}".format(self.hp_total_diff, self.distance, self.area)

    def apply(self, **kwargs):
        def get_msg(e):
            if self.hp_total_diff < 0:
                return "The {} is healed {} points".format(e.name, -self.hp_total_diff)
            else:
                return "The {} takes {} fire damage".format(e.name, self.hp_total_diff)

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
                    if self.hp_total_diff < 0:
                        results.extend(e.fighter.heal(-self.hp_total_diff))
                    else:
                        results.extend(e.fighter.take_damage(self.hp_total_diff))
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
                    if self.hp_total_diff < 0:
                        results.extend(e.fighter.heal(-self.hp_total_diff))
                    else:
                        results.extend(e.fighter.take_damage(self.hp_total_diff))
                    targets.append(e)
        return results
