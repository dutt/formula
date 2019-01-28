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

    def next_level(self):
        self.level_reached += 1
        self.monsters_killed_total += self.monsters_killed_level
        self.monsters_killed_level = 0
        self.xp_gathered_total += self.xp_gathered_this_level

    def monster_killed(self, monster):
        self.monsters_killed_level += 1
        if len(self.monsters_killed_per_level) < self.level_reached:
            self.monsters_killed_per_level.append([])
        self.monsters_killed_per_level[self.level_reached-1].append(monster)
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
