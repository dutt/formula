from components.ingredients import Ingredient

RECIPIES = [
    {
        "name" : "Craft inferno",
        "input" : [Ingredient.FIRE, Ingredient.FIRE],
        "output" : Ingredient.INFERNO
    },
    {
        "name" : "Craft firebolt",
        "input" : [Ingredient.FIRE, Ingredient.RANGE],
        "output" : Ingredient.FIREBOLT
    },
    {
        "name" : "Craft firespray",
        "input" : [Ingredient.FIRE, Ingredient.AREA],
        "output" : Ingredient.FIRESPRAY
    },
    {
        "name" : "Craft sleet",
        "input" : [Ingredient.WATER, Ingredient.EARTH],
        "output" : Ingredient.SLEET
    },
    {
        "name" : "Craft icebolt",
        "input" : [Ingredient.WATER, Ingredient.RANGE],
        "output" : Ingredient.ICEBOLT
    },
    {
        "name" : "Craft ice vortex",
        "input" : [Ingredient.WATER, Ingredient.AREA],
        "output" : Ingredient.ICE_VORTEX
    },
    {
        "name" : "Craft ice",
        "input" : [Ingredient.WATER, Ingredient.WATER],
        "output" : Ingredient.ICE
    },
    {
        "name" : "Craft vitality",
        "input" : [Ingredient.LIFE, Ingredient.LIFE],
        "output" : Ingredient.VITALITY
    },
    {
        "name" : "Craft rock",
        "input" : [Ingredient.EARTH, Ingredient.EARTH],
        "output" : Ingredient.ROCK
    },
    {
        "name" : "Craft magma",
        "input" : [Ingredient.EARTH, Ingredient.FIRE],
        "output" : Ingredient.MAGMA
    },
    {
        "name" : "Craft mud",
        "input" : [Ingredient.EARTH, Ingredient.WATER],
        "output" : Ingredient.MUD
    }
]

class IngredientCrafter():

    @staticmethod
    def match_recipes(ingredients, recipe):
        # the recipe isn't based on order, so go through each ingredient
        # and check that it has a corresponding ingredient in the inputs
        to_check = list(recipe)
        for ing in ingredients:
            found_idx = None
            for idx, check_ing in enumerate(to_check):
                if ing == check_ing:
                    found_idx = idx
                    break
            if found_idx is None:
                return False
            del to_check[found_idx]
        return True

    @staticmethod
    def valid_combination(ingredients):
        for recipe in RECIPIES:
            if IngredientCrafter.match_recipes(ingredients, recipe["input"]):
                return recipe["name"]
        return None

    @staticmethod
    def craft(ingredients):
        for recipe in RECIPIES:
            if IngredientCrafter.match_recipes(ingredients, recipe["input"]):
                return recipe["output"]
        return None
