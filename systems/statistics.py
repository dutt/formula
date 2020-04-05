class Statistics:
    def __init__(self):
        self.monsters_killed_total = 0
        self.monsters_killed_level = 0
        self.monsters_killed_per_level = []
        self.vials_thrown = []
        self.level_reached = 1
        self.xp_gathered_total = 0
        self.xp_gathered_this_level = 0
        self.looted_monsters = []
        self.moves = []
        self.start_time = None
        self.end_time = None

    def next_level(self):
        self.level_reached += 1
        self.monsters_killed_total += self.monsters_killed_level
        self.monsters_killed_level = 0
        self.xp_gathered_total += self.xp_gathered_this_level

    @property
    def total_play_time(self):
        playtime = self.end_time - self.start_time
        seconds = int(playtime.total_seconds())
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        return hours, minutes, seconds

    def monster_killed(self, monster):
        self.monsters_killed_level += 1
        while len(self.monsters_killed_per_level) < self.level_reached:
            self.monsters_killed_per_level.append([])
        self.monsters_killed_per_level[self.level_reached - 1].append(monster)
        self.xp_gathered_this_level += monster.fighter.xp

    def throw_vial(self, formula):
        self.vials_thrown.append(formula)

    @property
    def num_looted_monsters(self):
        return len(self.looted_monsters)

    def loot_monster(self, monster):
        self.looted_monsters.append(monster)

    @property
    def num_moves(self):
        return len(self.moves)

    def move_player(self, move):
        self.moves.append(move)

    @property
    def monsters_per_type_per_level(self):
        retr = [{} for _ in range(len(self.monsters_killed_per_level))]
        for idx, level in enumerate(self.monsters_killed_per_level):
            for monster in level:
                if monster.orig_name in retr[idx]:
                    retr[idx][monster.orig_name] += 1
                else:
                    retr[idx][monster.orig_name] = 1
        return retr

    @property
    def monsters_per_type(self):
        retr = {}
        for idx, level in enumerate(self.monsters_killed_per_level):
            for monster in level:
                if monster.orig_name in retr:
                    retr[monster.orig_name] += 1
                else:
                    retr[monster.orig_name] = 1
        return retr
