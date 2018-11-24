from messages import Message


class Shield:
    def __init__(self, level, strikebacks, owner):
        self.level = level
        self.max_level = level
        self.strikebacks = strikebacks
        self.owner = owner

    def on_hit(self, source, dmg, dmg_type):
        results = []
        if source:
            for sb in self.strikebacks:
                sb.apply(source)
                text = "Shield hits {} for {} {} damage".format(source.name, sb.stats.amount, sb.stats.dmg_type.name.lower())
                results.append({"message": Message(text)})
        actual_dmg = max(0, dmg - self.level)
        self.level = max(0, self.level - dmg)
        if self.level <= 0:
            results.append({"depleted": True})
        return results, actual_dmg
