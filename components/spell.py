import uuid

import tcod

from components.ingredients import Ingredient
from messages import Message


class Spell:
    EMPTY = None  # set in spell_engine.py

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.parse(**kwargs)

    @property
    def targeting_message(self):
        return Message("Targeting spell, dmg={}, range={}, area={}".format(self.damage, self.distance, self.area))

    def parse(self, **kwargs):
        self.spellidx = kwargs["spellidx"]
        self.slots = kwargs["slots"]
        self.cooldown = kwargs["cooldown"]
        self.damage = kwargs["damage"]
        self.distance = float(kwargs["distance"]) + 0.5  # for diagonal
        self.area = float(kwargs["area"]) + 0.5

    @property
    def text_repr(self):
        retr = ""
        for s in self.slots:
            if s == Ingredient.EMPTY:
                retr += ""
            elif s == Ingredient.FIRE:
                retr += "F"
            elif s == Ingredient.AREA:
                retr += "A"
            elif s == Ingredient.RANGE:
                retr += "R"
        return retr

    def apply(self, **kwargs):
        caster = kwargs.get("caster")
        target_x = kwargs.get("target_x")
        target_y = kwargs.get("target_y")
        entities = kwargs.get("entities")
        fov_map = kwargs.get("fov_map")
        results = []
        if caster.distance(target_x, target_y) > self.distance:
            results.append({"cast": False, "message": Message("Target out of range, spell not cast", tcod.yellow)})
            return results
        elif self.area < 1.5:  # no aoe
            for e in entities:
                if not e.fighter or not tcod.map_is_in_fov(fov_map, target_x, target_y):
                    continue
                if e.x == target_x and e.y == target_y:
                    msg = "Spell cast, the {} takes {} fire damage".format(e.name, self.damage)
                    results.append({"cast": True, "message": Message(msg), "targets": [e], "spell": self})
                    results.extend(e.fighter.take_damage(self.damage))
                    break
            else:
                results.append({"cast": False, "message": Message("No target"), "targets": [], "spell": self})
        else:  # aoe spell
            targets = []
            for e in entities:
                if not e.fighter or not tcod.map_is_in_fov(fov_map, target_x, target_y):
                    continue
                if e.distance(target_x, target_y) < self.area:
                    results.extend(e.fighter.take_damage(self.damage))
                    targets.append(e)
            results.append({"cast": True, "targets": targets, "spell": self, "message": Message("AOE spell cast")})
        return results
