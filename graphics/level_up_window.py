import random

import pygame

import config
from components.ingredients import Ingredient
from graphics.display_helpers import display_text, display_lines
from graphics.formula_window import FormulaWindow
from graphics.window import Window
from systems.input_handlers import EventType


class LevelUpWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.choices = []
        self.slots_message = "Bigger vials (+1 slot per vial)"
        self.formulas_message = "More vials (+1 prepared formula)"

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())
        header = ["You have expanded your skills and equipment, please choose:", ""]
        linediff = gfx_data.assets.font_message_height
        y = 3 * linediff
        display_lines(surface, gfx_data.assets.font_message, header, starty=y)

        y += 2 * linediff

        if not self.choices:
            if "level_" in config.conf.unlock_mode:
                all_choices = [self.slots_message, self.formulas_message]
                for upgrade in game_data.formula_builder.available_upgrades():
                    all_choices.append(upgrade.description)
                if config.conf.unlock_mode == "level_2random":
                    while len(self.choices) < 2:
                        self.choices = set(random.choices(all_choices, k=2))
                    self.choices = list(self.choices)
                else:
                    self.choices = all_choices
            else:
                self.choices = [self.slots_message, self.formulas_message]

        for idx, choice in enumerate(self.choices):
            text = str(choice)
            if idx == game_data.menu_data.currchoice:
                text += " <--"
            display_text(surface, text, gfx_data.assets.font_message, (50, y))
            y += linediff
        display_text(
            surface, "W/S to change selection, space to choose", gfx_data.assets.font_message, (50, 500),
        )
        gfx_data.main.blit(surface, self.pos.tuple())

    def get_ingredient_from_description(self, description):
        for i in Ingredient.all():
            if i.description == description:
                return i
        return None

    def apply_choice(self, choice, game_data):
        chosen = self.choices[choice]
        ingred = self.get_ingredient_from_description(chosen)
        if ingred:
            if ingred in Ingredient.upgrades():
                base = Ingredient.get_base_form(ingred)
                game_data.formula_builder.unlock_ingredient(ingred)
                game_data.formula_builder.replace_all(base, ingred)
            else:
                game_data.formula_builder.unlock_ingredient(ingred)
        elif chosen == self.slots_message:
            game_data.formula_builder.add_slot()
        elif chosen == self.formulas_message:
            game_data.formula_builder.add_formula()
        else:
            raise ValueError("Unknown choice in level up: {}".format(chosen))

    def prev_choice(self, game_data):
        game_data.menu_data.currchoice = max(0, game_data.menu_data.currchoice - 1)

    def next_choice(self, game_data):
        game_data.menu_data.currchoice = min(len(self.choices) - 1, game_data.menu_data.currchoice + 1)

    def handle_key(self, game_data, gfx_data, key_action):
        choice = key_action.get("choice")
        if choice:
            if choice < 0:
                self.prev_choice(game_data)
            else:
                self.next_choice(game_data)

        level_up = key_action.get(EventType.level_up)
        if level_up:
            self.apply_choice(game_data.menu_data.currchoice, game_data)
            game_data.player.caster.set_formulas(game_data.formula_builder.evaluate_entity(game_data.player))
            self.choices = []
            return self.close(game_data, next_window=FormulaWindow)

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(EventType.scroll_up)
        if scroll_up:
            self.prev_choice(game_data)
        scroll_down = mouse_action.get(EventType.scroll_down)
        if scroll_down:
            self.next_choice(game_data)
