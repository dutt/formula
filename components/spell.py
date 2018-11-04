import tcod

from messages import Message

class Spell:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.parse(**kwargs)

    @property
    def targeting_message(self):
        return Message("Targeting spell, dmg={}, range={}, area={}".format(self.damage, self.distance, self.area))

    def parse(self, **kwargs):
        self.damage = kwargs["damage"]
        self.distance = float(kwargs["distance"]) + 0.5 # for diagonal
        self.area = float(kwargs["area"]) + 0.5

    def apply(self, **kwargs):
        caster = kwargs.get("caster")
        target_x = kwargs.get("target_x")
        target_y = kwargs.get("target_y")
        entities = kwargs.get("entities")
        fov_map = kwargs.get("fov_map")
        results = []
        if caster.distance(target_x, target_y) > self.distance:
            results.append({"cast": False, "message": Message("Target out of range, spell not cast", tcod.yellow)})
            return  results
        elif self.area <= 1.5: # no aoe
            for e in entities:
                if not e.fighter or e == caster or not tcod.map_is_in_fov(fov_map, target_x, target_y):
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
                if not e.fighter or e == caster or not tcod.map_is_in_fov(fov_map, target_x, target_y):
                    continue
                if e.distance(target_x, target_y) < self.area:
                    results.extend(e.fighter.take_damage(self.damage))
                    targets.append(e)
            results.append({"cast": True, "targets":targets, "spell": self, "message": Message("AOE spell cast")})
        return results