import random

from systems.fov import initialize_fov
from graphics.assets import Assets
from map_related.map_file_loader import MapFileLoader
from map_related.tower_map_gen import TowerMapGenerator
from util import resource_path
from components.ingredients import Ingredient
from components.consumable import Firebomb, Freezebomb, CooldownClear, Teleporter
import config


class RunPlanner:
    def __init__(self, levels, player, constants, timesystem, run_tutorial):
        self.parts = levels // 3
        self.level_count = levels + 1
        self.levels = []
        self.player = player
        self.assets = Assets.get()
        self.constants = constants
        self.size = constants.map_size
        self.timesystem = timesystem
        self.current_level_index = None
        self.gen_level_idx = 0
        self.run_tutorial = run_tutorial

    def generate(self, game_state):
        if self.run_tutorial:
            self.levels.append(self.make_tutorial_map())
            self.gen_level_idx += 1

        for i in range(self.parts):
            self.levels.append(self.make_easy_map(self.gen_level_idx))
            self.gen_level_idx += 1

        for i in range(self.parts):
            self.levels.append(self.make_medium_map(self.gen_level_idx + i))
            self.gen_level_idx += 1

        for i in range(self.parts):
            self.levels.append(self.make_hard_map(self.gen_level_idx + i))
            self.gen_level_idx += 1

        # calculate average number of rooms
        # num_chunks = []
        # for i in range(0, 500):
        #    map, chunks = self.make_easy_map(i)
        #    num_chunks.append(len(chunks))
        # chunk_sum = sum(num_chunks)
        # print("average chunks: {}/{} = {}".format(chunk_sum, len(num_chunks), chunk_sum / len(num_chunks)))

        # self.levels.append(self.make_final_map(self.gen_level_idx + 1))
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

    def make_tutorial_map(self):
        m = MapFileLoader.make_map(self.constants, 0, resource_path("data/maps/tutorial"))
        m.tutorial = True
        return m

    def make_easy_map(self, current_level):
        monster_chances = {"any": 80, "thug": 40, "axe_thrower": 30, "dog_group": 30}
        ingredient_count = {
            Ingredient.FIRE: 2,
            Ingredient.WATER: 2,
            Ingredient.EARTH: 2,
            Ingredient.RANGE: 2,
            Ingredient.AREA: 2,
        }
        key_ratio = 0.4
        consumable_count = {Firebomb: 1, Freezebomb: 1, CooldownClear: 1, Teleporter: 1}
        return TowerMapGenerator.make_map(
            self.constants,
            current_level,
            monster_chances,
            key_ratio,
            ingredient_count=ingredient_count,
            consumable_count=consumable_count,
        )

    def sample_ingredients(self, ingredient_count, count, choices):
        for _ in range(count):
            choice = random.choice(choices)
            if not choice in ingredient_count:
                ingredient_count[choice] = 0
            ingredient_count[choice] += 1
        return ingredient_count

    def sample_all(
        self, fire_count, water_count, earth_count, life_count, modifier_count, basics=True,
    ):
        ingredient_count = {}

        all_fires = [Ingredient.INFERNO, Ingredient.FIREBOLT, Ingredient.FIRESPRAY]
        if basics:
            all_fires.append(Ingredient.FIRE)
        ingredient_count = self.sample_ingredients(ingredient_count, count=fire_count, choices=all_fires)

        all_waters = [Ingredient.SLEET, Ingredient.ICEBOLT, Ingredient.ICE_VORTEX]
        if basics:
            all_waters.append(Ingredient.WATER)
        ingredient_count = self.sample_ingredients(ingredient_count, count=water_count, choices=all_waters)

        all_earths = [Ingredient.ROCK, Ingredient.MUD, Ingredient.MAGMA]
        if basics:
            all_earths.append(Ingredient.EARTH)
        ingredient_count = self.sample_ingredients(ingredient_count, count=earth_count, choices=all_earths)

        all_lifes = [Ingredient.VITALITY]
        if basics:
            all_lifes.append(Ingredient.LIFE)
        ingredient_count = self.sample_ingredients(ingredient_count, count=life_count, choices=all_lifes)

        all_modifiers = [Ingredient.RANGE, Ingredient.AREA]
        if config.conf.trap:
            all_modifiers.append(Ingredient.TRAP)
        ingredient_count = self.sample_ingredients(ingredient_count, count=modifier_count, choices=all_modifiers)

        return ingredient_count

    def make_medium_map(self, current_level):
        monster_chances = {
            "any": 80,
            "mercenary": 40,
            "boar_group": 30,
            "rifleman": 30,
        }

        ingredient_count = self.sample_all(fire_count=2, water_count=2, earth_count=2, life_count=2, modifier_count=2)

        consumable_count = {Firebomb: 1, Freezebomb: 1, CooldownClear: 1, Teleporter: 1}
        key_ratio = 0.6
        return TowerMapGenerator.make_map(
            self.constants,
            current_level,
            monster_chances,
            key_ratio,
            ingredient_count=ingredient_count,
            consumable_count=consumable_count,
        )

    def make_hard_map(self, current_level):
        monster_chances = {
            "any": 90,
            "stalker": 40,
            "armored_bear_group": 30,
            "zapper": 30,
        }

        ingredient_count = self.sample_all(
            fire_count=3, water_count=3, earth_count=3, life_count=2, modifier_count=2, basics=False,
        )

        consumable_count = {Firebomb: 1, Freezebomb: 1, CooldownClear: 1, Teleporter: 1}
        key_ratio = 0.8
        return TowerMapGenerator.make_map(
            self.constants,
            current_level,
            monster_chances,
            key_ratio,
            ingredient_count=ingredient_count,
            consumable_count=consumable_count,
        )

    def make_final_map(self, current_level):
        return MapFileLoader.make_map(self.constants, current_level, resource_path("data/maps/final"))
