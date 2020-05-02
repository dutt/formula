class Effect:
    def __init__(self, rounds, applicator, stats_func, colorize_visual_func=None):
        self.rounds = rounds
        self.rounds_left = rounds
        self.applicator = applicator
        self.stats_func = stats_func
        if colorize_visual_func:
            self.colorize_visual = colorize_visual_func
        else:
            self.colorize_visual = self.no_color

    def apply(self, target):
        return self.applicator(target)

    @property
    def stats(self):
        return self.stats_func()

    def tick(self):
        self.rounds_left -= 1

    @property
    def valid(self):
        return self.rounds_left > 0

    def no_color(self):
        pass

    def serialize(self):
        retr = {
            "rounds": self.rounds,
        }
        stats = self.stats_func()
        for key in stats:
            if key in ["type", "dmg_type"]:
                retr[f"stats.{key}"] = stats[key].name
            else:
                retr[f"stats.{key}"] = stats[key]
        return retr
