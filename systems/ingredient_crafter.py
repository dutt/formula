from components.ingredients import Ingredient

RECIPIES = [
    {
        "name" : "From fire to inferno",
        "input" : [Ingredient.FIRE, Ingredient.FIRE],
        "output" : Ingredient.INFERNO
    }
]

class IngredientCrafter():
    @staticmethod
    def valid_combination(ingredients):
        for recipe in RECIPIES:
            if ingredients == recipe["input"]:
                return recipe["name"]
        return None

    @staticmethod
    def craft(ingredients):
        for recipe in RECIPIES:
            if ingredients == recipe["input"]:
                return recipe["output"]
        return None
