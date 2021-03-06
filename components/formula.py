import tcod

from components.effect_type import EffectType
from systems.messages import Message


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
        self.targeted = kwargs["targeted"]
        self.suboptimal = kwargs["suboptimal"]
        self.trap = kwargs["trap"]

        self.targeting_message_text = self.text_stats_text = self.applied_text = None
        self.set_texts()

    def serialize(self):
        return {
            "slots": [s.name for s in self.slots],
            "distance": self.distance,
            "area": self.area,
            "effects": [e.serialize() for e in self.effects],
            "targeted": self.targeted,
            "suboptimal": self.suboptimal,
            "trap": self.trap,
        }

    def set_texts(self):
        text_msg = ""
        applied_msg = ""
        for e in self.effects:
            e_text_message, e_applied_msg = self.get_effect_messages(e)
            text_msg += e_text_message
            applied_msg += e_applied_msg
        postfix = "range={}, area={}".format(self.distance, self.area)
        if text_msg:
            if self.trap:
                self.targeting_message_text = "Place trap, {}, area={}".format(text_msg[:-2], self.area)
            else:
                self.targeting_message_text = "Targeting, {}, {}".format(text_msg[:-2], postfix)
            self.text_stats_text = "{}, {}".format(text_msg[:-2], postfix)
            self.applied_text = "{} " + applied_msg[:-2]
        else:
            self.targeting_message_text = ""
            self.text_stats_text = ""
            self.applied_text = ""

    def get_effect_messages(self, effect):
        text_msg = ""
        applied_msg = ""
        stats = effect.stats
        if stats.type == EffectType.DAMAGE:
            name = stats.dmg_type.name.lower()
            text_msg = "{} {} damage, ".format(stats.amount, name)
            applied_msg = "hurt, {} {} damage, ".format(stats.amount, name)
        elif stats.type == EffectType.HEALING:
            text_msg = "{} healing, ".format(stats.amount)
            applied_msg = "healed for {}, ".format(stats.amount)
        elif stats.type == EffectType.SLOW:
            text_msg = "slow for {} rounds, ".format(stats.rounds)
            applied_msg = "slowed for {} rounds, ".format(stats.rounds)
        elif stats.type == EffectType.DEFENSE:
            text_msg = "shield resisting {} damage".format(stats.level)
            applied_msg = "shielded for {} damage".format(stats.level)
            if stats.strikebacks:
                text_msg += " and dealing "
                applied_msg += ", shield dealing "
                for sb in stats.strikebacks:
                    sb_txt, _ = self.get_effect_messages(sb)
                    text_msg += sb_txt
                    applied_msg += applied_msg
            else:
                text_msg += ", "
                applied_msg += ", "
        return text_msg, applied_msg

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
            return self.applied_text.format(e.name_with_prep)

        caster = kwargs.get("caster")
        target_x = kwargs.get("target_x")
        target_y = kwargs.get("target_y")
        entities = kwargs.get("entities")
        game_map = kwargs.get("game_map")
        fov_map = kwargs.get("fov_map")
        triggered_trap = kwargs.get("triggered_trap")
        results = []

        if caster.distance(target_x, target_y) > self.distance:
            results.append({"cast": False, "message": Message("Target out of range", tcod.yellow)})
            return results
        elif self.trap and not triggered_trap:
            game_map.tiles[target_x][target_y].trap = self
            results.append(
                {"cast": True, "message": Message("Formula cast as trap"), "formula": self,}
            )
        elif self.area < 1.5:  # no aoe
            for e in entities:
                if not e.fighter or not tcod.map_is_in_fov(fov_map, target_x, target_y):
                    continue
                if e.pos.x == target_x and e.pos.y == target_y:
                    results.append(
                        {"cast": True, "message": Message(get_msg(e)), "targets": [e], "formula": self,}
                    )
                    for effect in self.effects:
                        results.extend(effect.apply(e))
                        if effect.stats.rounds > 1:
                            e.add_effect(effect, effect.stats.rounds)
                    break
            else:
                results.append(
                    {"cast": False, "message": Message("No target"), "targets": [], "formula": self,}
                )
        else:  # aoe formula
            targets = []
            results.append(
                {"cast": True, "targets": targets, "formula": self, "message": Message("Splash vial thrown"),}
            )
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
