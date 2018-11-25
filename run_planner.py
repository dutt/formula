from gamemap import GameMap
from random_utils import from_dungeon_level

class RunPlanner:
    def __init__(self, levels, player, assets, constants, timesystem):
        parts = levels // 3
        self.levels = []
        self.player = player
        self.assets = assets
        self.constants = constants
        self.size = constants.map_size

        current = 0
        for i in range(parts):
            self.levels.append(self.make_easy_map(i))
        current += parts
        for i in range(parts):
            self.levels.append(self.make_medium_map(current+i))
        current += parts
        for i in range(parts):
            self.levels.append(self.make_hard_map(current+i))
        current += parts
        self.levels.append(self.make_final_map(current))
        self.current_level_index = None
        self.timesystem = timesystem
        self.activate_next_level()


    @property
    def current_map(self):
        return self.levels[self.current_level_index]

    @property
    def has_next(self):
        return self.current_level_index < len(self.levels) - 1

    def activate_next_level(self):
        if self.current_level_index is not None:
            for e in self.current_map.entities:
                if e.active:
                    self.timesystem.release(e)
            self.current_level_index += 1
        else:
            self.current_level_index = 0
        self.levels[self.current_level_index].entities.insert(0, self.player)
        self.player.pos = self.current_map.player_pos
        for e in self.current_map.entities:
            self.timesystem.register(e)
        return self.current_map

    def make_easy_map(self, current_level):
        monster_chances = { "ghost" : 60,
                            "chucker" : 40}
        map = GameMap(self.size, self.assets, current_level, self.constants, monster_chances)
        return map

    def make_medium_map(self, current_level):
        monster_chances = {"ghost": 90,
                           "demon": 10}
        return GameMap(self.size, self.assets, current_level, self.constants, monster_chances)

    def make_hard_map(self, current_level):
        monster_chances = {"ghost": 90,
                           "demon": 10}
        return GameMap(self.size, self.assets, current_level, self.constants, monster_chances)

    def make_final_map(self, current_level):
        monster_chances = {"ghost": 90,
                           "demon": 10}
        return GameMap(self.size, self.assets, current_level, self.constants, monster_chances)
