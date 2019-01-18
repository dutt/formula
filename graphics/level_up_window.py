import random

import pygame

import config
from graphics.display_helpers import display_text, display_lines
from graphics.window import Window
from input_handlers import Event
from components.ingredients import Ingredient

class LevelUpWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.choices = []


    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())
        header = [
            "You have expanded your skills and equipment, please choose:",
            ""
        ]
        linediff = 15
        y = 3 * linediff
        display_lines(surface, gfx_data.assets.font_message, header, starty=y)

        y += 2 * linediff

        if self.choices == []:
            if config.conf.unlock_mode == "level":
                all_choices = [ "Bigger vials (+1 slot per vial)",
                                "More vials (+1 prepared formula)",
                                Ingredient.FIRE if not game_data.formula_builder.ingredient_unlocked(Ingredient.FIRE) else None,
                                Ingredient.RANGE if not game_data.formula_builder.ingredient_unlocked(Ingredient.RANGE) else None,
                                Ingredient.AREA if not game_data.formula_builder.ingredient_unlocked(Ingredient.AREA) else None,
                                Ingredient.COLD if not game_data.formula_builder.ingredient_unlocked(Ingredient.COLD) else None,
                                Ingredient.LIFE if not game_data.formula_builder.ingredient_unlocked(Ingredient.LIFE) else None,
                                Ingredient.SHIELD if not game_data.formula_builder.ingredient_unlocked(Ingredient.SHIELD) else None]
                clean_choices = [c for c in all_choices if c]
                self.choices = random.choices(clean_choices, k=2)
            else:
                self.choices = [
                    "Bigger vials (+1 slot per vial)",
                    "More vials (+1 prepared formula)"
                ]

        for idx, choice in enumerate(self.choices):
            text = str(choice)
            if idx == game_data.menu_data.currchoice:
                text += "<--"
            display_text(surface, text, gfx_data.assets.font_message, (50, y))
            y += linediff
        display_text(surface, "W/S to change selection, space to choose", gfx_data.assets.font_message, (50, 300))
        gfx_data.main.blit(surface, self.pos.tuple())

    def apply_choice(self, choice, game_data):
        chosen = self.choices[choice]
        if chosen == "Bigger vials (+1 slot per vial)":
            game_data.formula_builder.add_slot()
        elif chosen == "More vials (+1 prepared formula)":
            game_data.formula_builder.add_formula()
        elif chosen in [Ingredient.FIRE,
                        Ingredient.RANGE,
                        Ingredient.AREA,
                        Ingredient.COLD,
                        Ingredient.LIFE,
                        Ingredient.SHIELD]:
            game_data.formula_builder.unlock_ingredient(chosen)
        else:
            raise ValueError("Unknown choice in level up: {}".format(chosen))

    def handle_key(self, game_data, gfx_data, key_action):
        choice = key_action.get("choice")
        if choice:
            game_data.menu_data.currchoice += choice
            if game_data.menu_data.currchoice < 0:
                game_data.menu_data.currchoice = 0
            elif game_data.menu_data.currchoice > 1:
                game_data.menu_data.currchoice = 1

        level_up = key_action.get(Event.level_up)
        if level_up:
            self.apply_choice(game_data.menu_data.currchoice, game_data)

            self.choices = []
            self.close(game_data)
