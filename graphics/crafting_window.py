import pygame

from graphics.display_helpers import display_text
from graphics.window import Window
from graphics.textwindow import TextWindow
from systems.input_handlers import EventType
from systems.ingredient_crafter import IngredientCrafter
from components.ingredients import Ingredient
from systems.messages import Message
from util import Pos, resource_path


class CraftingHelpWindow(TextWindow):
    PATH = resource_path("data/help/crafting_window.txt")

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, path=CraftingHelpWindow.PATH, next_window=None)


class CraftingSlot:
    def __init__(self, pos, index=None):
        self.index = index
        self.pos = pos
        self.ingredient = Ingredient.EMPTY

    def draw(self, surface, game_data, gfx_data, selected_slot):
        assert self.ingredient, f"{self.index} {self.ingredient}"
        text = "[" + self.ingredient.name.upper() + "]"
        if self.index is not None and selected_slot == self.index:
            text += " <--"
        display_text(surface, text, gfx_data.assets.font_message, self.pos.tuple())


class CraftingWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.current_slot = 0
        self.slot_count = 2
        self.setup_slots()
        self.ingredient_counts = {}

    def setup_slots(self):
        self.input_slots = []
        for idx in range(self.slot_count):
            self.input_slots.append(CraftingSlot(Pos(100, 100 + idx * 40), index=idx))

        self.output_slot = CraftingSlot(Pos(400, 100 + ((40 * idx) // 2)))

    def draw_ingredient_choices(self, surface, game_data, gfx_data):
        ingredient_to_key_map = [
            [Ingredient.EMPTY, "Q"],
            [Ingredient.WATER, "W"],
            [Ingredient.FIRE, "E"],
            [Ingredient.RANGE, "R"],
            [Ingredient.AREA, "A"],
            [Ingredient.LIFE, "S"],
            [Ingredient.EARTH, "D"],
        ]
        x_base = 100
        y_base = 200
        ing_count = 0
        for ing, key in ingredient_to_key_map:
            if ing == Ingredient.EMPTY:
                text = ing.name.capitalize()
            else:
                count = game_data.ingredient_storage.total_count(ing)
                if ing in self.ingredient_counts:
                    count -= self.ingredient_counts[ing]
                text = "{} : {}".format(ing.name.capitalize(), count)
            display_text(surface, text, gfx_data.assets.font_message, (x_base, y_base))
            display_text(surface, key, gfx_data.assets.font_message, (x_base, y_base + 30))
            x_base += 90
            ing_count += 1
            if ing_count > 3:
                y_base += 60
                x_base = 100
                ing_count = 0

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())

        for s in self.input_slots:
            s.draw(surface, game_data, gfx_data, self.current_slot)

        self.output_slot.draw(surface, game_data, gfx_data, self.current_slot)

        self.draw_ingredient_choices(surface, game_data, gfx_data)

        display_text(
            surface, "Press Space to confirm, Escape to quit, Tab for help", gfx_data.assets.font_message, (140, 500),
        )

        gfx_data.main.blit(surface, self.pos.tuple())

    def change_slot(self, diff):
        self.current_slot = (self.current_slot + diff) % self.slot_count

    def update_ingredient_counts(self, inputs):
        self.ingredient_counts = {}
        for ing in inputs:
            if ing not in self.ingredient_counts:
                self.ingredient_counts[ing] = 0
            self.ingredient_counts[ing] += 1

    def update_output_slot(self, inputs):
        if IngredientCrafter.valid_combination(inputs):
            self.output_slot.ingredient = IngredientCrafter.craft(inputs)
        else:
            self.output_slot.ingredient = Ingredient.EMPTY

    def set_slot(self, game_data, ingredient):
        if ingredient == Ingredient.EMPTY:
            self.input_slots[self.current_slot].ingredient = ingredient
        else:
            count = game_data.ingredient_storage.total_count(ingredient)
            if ingredient in self.ingredient_counts:
                count -= self.ingredient_counts[ingredient]

            if count > 0:
                self.input_slots[self.current_slot].ingredient = ingredient
                self.change_slot(1)

        inputs = [slot.ingredient for slot in self.input_slots]
        self.update_output_slot(inputs)
        self.update_ingredient_counts(inputs)

    def has_all_needed(self, ingredients, game_data):
        counts = {}
        for i in ingredients:
            if i not in counts:
                counts[i] = 0
            counts[i] += 1
        for i, num in counts.items():
            if num > game_data.ingredient_storage.count_left(i, game_data.formula_builder):
                return False
        return True

    def apply_craft(self, game_data):
        if self.output_slot.ingredient == Ingredient.EMPTY:
            return  # no crafting
        inputs = [slot.ingredient for slot in self.input_slots]
        game_data.ingredient_storage.remove_multiple(inputs)
        game_data.ingredient_storage.add(self.output_slot.ingredient)

        if not self.has_all_needed(inputs, game_data):
            for s in self.input_slots:  # lacking one, reset
                s.ingredient = Ingredient.EMPTY
            inputs = [slot.ingredient for slot in self.input_slots]
            self.update_ingredient_counts(inputs)

        logname = self.output_slot.ingredient.name.capitalize()
        return {"message": Message(f"You crafted a {logname}")}

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(EventType.exit)
        if do_quit:
            return self.close(game_data, activate_for_new_state=True)

        next_slot = key_action.get("next_slot")
        if next_slot:
            self.change_slot(next_slot)

        ingredient = key_action.get("ingredient")
        if ingredient:
            self.set_slot(game_data, ingredient)

        apply = key_action.get("apply")
        if apply:
            return self.apply_craft(game_data)

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(EventType.scroll_up)
        if scroll_up:
            self.change_slot(-1)

        scroll_down = mouse_action.get(EventType.scroll_down)
        if scroll_down:
            self.change_slot(1)
