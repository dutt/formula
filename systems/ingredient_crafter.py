from components.ingredients import Ingredient
import config

RECIPIES = []


class IngredientCrafter:
    @staticmethod
    def setup():
        RECIPIES.append(
            {"name": "Craft inferno", "input": [Ingredient.FIRE, Ingredient.FIRE], "output": Ingredient.INFERNO,}
        )
        RECIPIES.append(
            {"name": "Craft firebolt", "input": [Ingredient.FIRE, Ingredient.RANGE], "output": Ingredient.FIREBOLT,}
        )
        RECIPIES.append(
            {"name": "Craft firespray", "input": [Ingredient.FIRE, Ingredient.AREA], "output": Ingredient.FIRESPRAY,}
        )
        RECIPIES.append(
            {"name": "Craft sleet", "input": [Ingredient.WATER, Ingredient.EARTH], "output": Ingredient.SLEET,}
        )
        RECIPIES.append(
            {"name": "Craft icebolt", "input": [Ingredient.WATER, Ingredient.RANGE], "output": Ingredient.ICEBOLT,}
        )
        RECIPIES.append(
            {"name": "Craft ice vortex", "input": [Ingredient.WATER, Ingredient.AREA], "output": Ingredient.ICE_VORTEX,}
        )
        RECIPIES.append(
            {"name": "Craft ice", "input": [Ingredient.WATER, Ingredient.WATER], "output": Ingredient.ICE,}
        )
        RECIPIES.append(
            {"name": "Craft vitality", "input": [Ingredient.LIFE, Ingredient.LIFE], "output": Ingredient.VITALITY,}
        )
        RECIPIES.append(
            {"name": "Craft rock", "input": [Ingredient.EARTH, Ingredient.EARTH], "output": Ingredient.ROCK,}
        )
        RECIPIES.append(
            {"name": "Craft magma", "input": [Ingredient.EARTH, Ingredient.FIRE], "output": Ingredient.MAGMA,}
        )
        RECIPIES.append(
            {"name": "Craft mud", "input": [Ingredient.EARTH, Ingredient.WATER], "output": Ingredient.MUD,}
        )
        if config.conf.trap:
            RECIPIES.append(
                {"name": "Craft trap", "input": [Ingredient.EARTH, Ingredient.RANGE], "output": Ingredient.TRAP,}
            )

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
