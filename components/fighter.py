import tcod

from messages import Message


class Fighter:
    def __init__(self, hp, defense, power, xp=0):
        self.hp = self.base_max_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.owner = None

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

    def take_damage(self, amount):
        assert amount > 0
        results = []
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
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
            results.extend(target.fighter.take_damage(dmg))
        else:
            text = "{} attacks {} but is too weak to hurt".format(self.owner.name, target.name)
            results.append({"message": Message(text, tcod.white)})
        return results
