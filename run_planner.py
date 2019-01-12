from fov import initialize_fov
from graphics.assets import Assets
from map_related.map_file_loader import MapFileLoader
from map_related.tower_map_gen import TowerMapGenerator
from util import resource_path


class RunPlanner:
    def __init__(self, levels, player, constants, timesystem):
        self.parts = levels // 3
        self.level_count = levels
        self.levels = []
        self.player = player
        self.assets = Assets.get()
        self.constants = constants
        self.size = constants.map_size
        self.timesystem = timesystem
        self.current_level_index = None
        self.gen_level_idx = 0

    def generate(self, game_state):
        for i in range(self.parts):
           self.levels.append(self.make_easy_map(self.gen_level_idx + 1))
           self.gen_level_idx += 1

        for i in range(self.parts):
            self.levels.append(self.make_medium_map(self.gen_level_idx + i))
            self.gen_level_idx += 1

         for i in range(self.parts):
            self.levels.append(self.make_hard_map(self.gen_level_idx + i))
            self.gen_level_idx += 1

        self.levels.append(self.make_final_map(self.gen_level_idx + 1))
        self.gen_level_idx += 1
        game_state.map = self.levels[0]
        game_state.fov_map = initialize_fov(game_state.map)
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
        monster_chances = {"any": 80,
                           "thug": 40,
                           "axe_thrower": 20,
                           "dog_group": 20}
        return TowerMapGenerator.make_map(self.constants, current_level, monster_chances)

    def make_medium_map(self, current_level):
        monster_chances = {"any": 90,
                           "mercenary": 40,
                           "boar_group": 20,
                           "rifleman": 20}
        return TowerMapGenerator.make_map(self.constants, current_level, monster_chances)

    def make_hard_map(self, current_level):
        monster_chances = {"any": 95,
                           "stalker": 40,
                           "armored_bear_group": 20,
                           "zapper": 20}
        return TowerMapGenerator.make_map(self.constants, current_level, monster_chances)

    def make_final_map(self, current_level):
        return MapFileLoader.make_map(self.constants, current_level, resource_path("data/maps/final"))
