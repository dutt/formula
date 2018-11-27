from components.damage_type import DamageType
from components.effect_type import EffectType
from messages import Message


class Shield:
    def __init__(self, level, strikebacks, owner, distance):
        self.level = level
        self.max_level = level
        self.strikebacks = strikebacks
        self.owner = owner
        self.distance = distance

    def on_hit(self, source, dmg, dmg_type):
        results = []
        if source and self.owner.distance_to(source) <= self.distance:
            for sb in self.strikebacks:
                sb.apply(source)
                text = "Shield hits {} for {} {} damage".format(source.name, sb.stats.amount,
                                                                sb.stats.dmg_type.name.lower())
                results.append({"message": Message(text)})
        actual_dmg = max(0, dmg - self.level)
        self.level = max(0, self.level - dmg)
        if self.level <= 0:
            results.append({"depleted": True})
            results.append({"message": Message("Your shield has been depleted")})
        return results, actual_dmg

    @property
    def color(self):
        alpha = 150
        if not self.strikebacks:
            return 0, 150, 150, alpha  # yellow tinge
        else:
            r = 100
            g = 100
            b = 100
            step = 30
            for sb in self.strikebacks:
                if sb.stats.type != EffectType.DAMAGE:
                    continue
                if sb.stats.dmg_type == DamageType.FIRE:
                    r += step
                elif sb.stats.dmg_type == DamageType.COLD:
                    b += step
            return r, g, b, alpha
