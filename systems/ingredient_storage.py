from components.ingredients import Ingredient
import config


class IngredientStorage:
    def __init__(self):
        self.counts = self.initialize_counts()

    def initialize_counts(self):
        retr = {}
        for ing in Ingredient.all():
            retr[ing] = 0
        return retr

    def add(self, ingredient):
        self.counts[ingredient] += 1

    def add_multiple(self, ingredient_counts):
        for ing, count in ingredient_counts.items():
            self.counts[ing] += count

    def remove_multiple(self, ingredients):
        for ing in ingredients:
            self.counts[ing] -= 1

    def count_left(self, ingredient, formula_builder):
        if config.conf.crafting:
            return self.count_left_crafting(ingredient, formula_builder)
        else:
            return self.count_left_nocrafting(ingredient, formula_builder)

    def count_left_crafting(self, ingredient, formula_builder):
        max_count = self.counts[ingredient]
        count = 0
        for formula_index in range(formula_builder.num_formula):
            slots = formula_builder.slots_for_formula(formula_index)
            for s in slots:
                if s == ingredient:
                    count += 1
        # assert count <= max_count, f"count: {count}, max_count {max_count}"
        return max_count - count

    def count_left_nocrafting(self, ingredient, formula_builder):
        ingredient_base = ingredient.get_base_form()
        max_count = self.counts[ingredient_base]
        count = 0
        for formula_index in range(formula_builder.num_formula):
            slots = formula_builder.slots_for_formula(formula_index)
            for s in slots:
                if s.get_base_form() == ingredient_base:
                    count += 1
        assert count <= max_count, f"count: {count}, max_count {max_count}"
        return max_count - count

    def total_count(self, ingredient):
        return self.counts[ingredient.get_base_form()]

    def remaining(self, formula_builder=None):
        retr = {}
        if formula_builder:
            for ing in self.counts.keys():
                retr[ing] = self.count_left(ing, formula_builder)
        else:
            for ing, count in self.counts.items():
                if count > 0:
                    retr[ing] = count
        return retr
