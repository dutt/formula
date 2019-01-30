import tcod

from components.damage_type import DamageType
from messages import Message


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
        results = []
        if self.shield:
            shield_results, actual_dmg = self.shield.on_hit(source, dmg, dmg_type)
            results.extend(shield_results)
            dmg = actual_dmg
            for res in shield_results:
                if res.get("depleted"):
                    self.shield = None
        self.hp = max(0, self.hp - dmg)
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
