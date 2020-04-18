from components.ingredients import Ingredient

class IngredientStorage:
    def __init__(self):
        self.counts = self.initialize_counts()

    def initialize_counts(self):
        retr = {}
        for ing in Ingredient.basics():
            retr[ing] = 0
        return retr

    def add(self, ingredient):
        self.counts[ingredient] += 1

    def add_multiple(self, ingredient_counts):
        for ing, count in ingredient_counts.items():
            self.counts[ing] += count

    def count_left(self, ingredient, formula_builder):
        ingredient_base = ingredient.get_base_form()
        max_count = self.counts[ingredient_base]
        count = 0
        for formula_index in range(formula_builder.num_formula):
            slots = formula_builder.slots_for_formula(formula_index)
            for s in slots:
                if s.get_base_form() == ingredient_base:
                    count += 1
        assert count <= max_count
        return max_count - count
