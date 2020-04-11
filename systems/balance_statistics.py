import json

from graphics.assets import Assets
from systems.monster_generator import get_monster
from systems.formula_builder import FormulaBuilder
from map_related.gamemap import GameMap
from components.ingredients import Ingredient, IngredientState
from components.effect_type import EffectType

from util import Rect, Size

def get_monsters(level):
    game_map = GameMap(Size(10, 10), dungeon_level=1)
    def helper(name):
        room = Rect(2, 2, 10, 10)
        return get_monster(0, 0, game_map, room, name, [])[0]

    if level == 1:
        monster_names = [
            "thug",
            "axe_thrower",
            "dog_group",
        ]
    elif level == 2:
        monster_names = [
            "mercenary",
            "rifleman",
            "boar_group"
        ]
    else:
        raise ValueError(f"No monsters specified for level {level}")
    retr = []
    for name in monster_names:
        retr.append(helper(name))
    return retr

def get_formula_stats():
    ingredient_lists = [
        # fire
        [Ingredient.EMPTY, Ingredient.FIRE, Ingredient.FIRE],
        [Ingredient.FIRE] * 3,
        [Ingredient.FIRE, Ingredient.FIRE, Ingredient.RANGE],
        [Ingredient.FIRE, Ingredient.RANGE, Ingredient.RANGE],

        # water
        [Ingredient.WATER] * 3,
        [Ingredient.EMPTY, Ingredient.WATER, Ingredient.WATER],
        [Ingredient.WATER, Ingredient.RANGE, Ingredient.RANGE],

        # fire upgrade
        [Ingredient.INFERNO, Ingredient.EMPTY, Ingredient.EMPTY],
        [Ingredient.INFERNO, Ingredient.INFERNO, Ingredient.EMPTY],
        [Ingredient.INFERNO] * 3,


        #
    ]

    builder = FormulaBuilder(10, 10, run_tutorial=False)
    formulas = [builder.evaluate_formula(f, 0, IngredientState(), caster="bob")[0] for f in ingredient_lists]
    formula_data = [f.serialize() for f in formulas]
    return formula_data

def calculate_results(monsters, formula_data):
    retr = []
    for m in monsters:
        for fd in formula_data:
            if len(fd["effects"]) == 1:
                data = fd["effects"][0]
                data["stats.type"] == EffectType.DAMAGE.name
                dmg = data["stats.amount"]
            else:
                for effect_data in fd["effects"]:
                    if effect_data["stats.type"] != EffectType.DAMAGE.name:
                        continue
                    dmg = effect_data["stats.amount"]
                    break
            assert dmg
            retr.append((m, fd, dmg >= m.fighter.max_hp))
    return retr

def print_stats():
    Assets.setup(mock=True)
    level = 1
    monsters = get_monsters(level=level)
    formula_stats = get_formula_stats()
    results = calculate_results(monsters, formula_stats)
    for r in results:
        m, fd, res = r
        text = "{}, {}, {}".format(m.name, fd["slots"], res)
        print(text)
