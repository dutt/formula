import tcod

from components.damage_type import DamageType
from systems.messages import Message


from graphics.visual_effect import VisualEffectSystem
from util import Pos
from graphics.assets import Assets
from graphics.constants import colors

class Fighter:
    def __init__(self, hp, defense, power, xp=0, dmg_type=DamageType.PHYSICAL, resistances=None, immunities=None,
                 shield=None):
        self.hp = self.base_max_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.owner = None
        self.dmg_type = dmg_type
        self.resistances = resistances if resistances else []
        self.immunities = immunities if immunities else []
        self.shield = shield
        self.killed_by = None

    def show_on_hit(self, dmg):
        above = Pos(self.owner.pos.x, self.owner.pos.y - 1)

        text_surface = [Assets.get().font_title.render(str(dmg), True, colors.RED)]
        VisualEffectSystem.get().add_temporary(self.owner.pos, above, lifespan=0.5, asset=text_surface,
                                               color=colors.RED)
    @property
    def max_hp(self):
        bonus = 0
        return self.base_max_hp + bonus

    @property
    def defense(self):
        bonus = 0
        return self.base_defense + bonus

    @property
    def power(self):
        bonus = 0
        return self.base_power + bonus

    def take_damage(self, source, dmg, dmg_type):
        assert dmg > 0
        assert source
        results = []
        if self.shield:
            shield_results, actual_dmg = self.shield.on_hit(source, dmg, dmg_type)
            results.extend(shield_results)
            dmg = actual_dmg
            for res in shield_results:
                if res.get("depleted"):
                    self.shield = None
        self.hp = max(0, self.hp - dmg)

        if dmg > 0:
            self.show_on_hit(dmg)

        if self.hp <= 0:
            self.killed_by = source
            results.append({"dead": self.owner, "xp": self.xp})
        return results

    def heal(self, amount):
        assert amount > 0
        self.hp = min(self.max_hp, self.hp + amount)
        return []

    def attack(self, target):
        results = []
        dmg = self.power - target.fighter.defense
        if dmg > 0:
            text = "{} attacks {} for {}".format(self.owner.name, target.name, dmg)
            results.append({"message": Message(text, tcod.white)})
            results.extend(target.fighter.take_damage(self.owner, dmg, self.dmg_type))
        else:
            text = "{} attacks {} but is too weak to hurt".format(self.owner.name, target.name)
            results.append({"message": Message(text, tcod.white)})
        return results
