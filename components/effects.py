class EffectTag:
    HP_DIFF = "hp_diff"


class Effect:
    def __init__(self, rounds, tag, effect_func):
        self.rounds = rounds
        self.rounds_left = rounds
        self.tag = tag
        self.effect_func = effect_func

    def apply(self):
        return self.effect_func()

    def tick(self):
        self.rounds_left -= 1

    @property
    def valid(self):
        return self.rounds_left > 0
