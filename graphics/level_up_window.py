import random

import pygame

import config
from graphics.display_helpers import display_text, display_lines
from graphics.window import Window
from input_handlers import Event
from graphics.formula_window import FormulaWindow
from components.ingredients import Ingredient


class LevelUpWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.choices = []
        self.slots_message = "Bigger vials (+1 slot per vial)"
        self.formulas_message = "More vials (+1 prepared formula)"

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

        if not self.choices:
            if "level_" in config.conf.unlock_mode:
                all_choices = [self.slots_message,
                               self.formulas_message]
                if not game_data.formula_builder.ingredient_unlocked(Ingredient.FIRE):
                    all_choices.append(Ingredient.FIRE.description)
                else:
                    inferno_unlocked = game_data.formula_builder.ingredient_unlocked(Ingredient.INFERNO)
                    firebolt_unlocked = game_data.formula_builder.ingredient_unlocked(Ingredient.FIREBOLT)
                    firespray_unlocked = game_data.formula_builder.ingredient_unlocked(Ingredient.FIRESPRAY)
                    if not inferno_unlocked and not firebolt_unlocked and not firespray_unlocked:
                        all_choices.extend([Ingredient.INFERNO.description,
                                            Ingredient.FIREBOLT.description,
                                            Ingredient.FIRESPRAY.description])
                if not game_data.formula_builder.ingredient_unlocked(Ingredient.RANGE):
                    all_choices.append(Ingredient.RANGE.description)
                if not game_data.formula_builder.ingredient_unlocked(Ingredient.AREA):
                    all_choices.append(Ingredient.AREA.description)
                if not game_data.formula_builder.ingredient_unlocked(Ingredient.COLD):
                    all_choices.append(Ingredient.COLD.description)
                if not game_data.formula_builder.ingredient_unlocked(Ingredient.LIFE):
                    all_choices.append(Ingredient.LIFE.description)
                if not game_data.formula_builder.ingredient_unlocked(Ingredient.SHIELD):
                    all_choices.append(Ingredient.SHIELD.description)
                if config.conf.unlock_mode == "level_2random":
                    while len(self.choices) < 2:
                        self.choices = set(random.choices(all_choices, k=2))
                    self.choices = list(self.choices)
                else:
                    self.choices = all_choices
            else:
                self.choices = [
                    self.slots_message,
                    self.formulas_message
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
        if chosen == self.slots_message:
            game_data.formula_builder.add_slot()
        elif chosen == self.formulas_message:
            game_data.formula_builder.add_formula()
        elif chosen == Ingredient.FIRE.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.FIRE)
        elif chosen == Ingredient.RANGE.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.RANGE)
        elif chosen == Ingredient.AREA.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.AREA)
        elif chosen == Ingredient.COLD.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.COLD)
        elif chosen == Ingredient.LIFE.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.LIFE)
        elif chosen == Ingredient.SHIELD.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.SHIELD)
        elif chosen == Ingredient.INFERNO.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.INFERNO)
        elif chosen == Ingredient.FIREBOLT.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.FIREBOLT)
        elif chosen == Ingredient.FIRESPRAY.description:
            game_data.formula_builder.unlock_ingredient(Ingredient.FIRESPRAY)
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

        level_up = key_action.get(Event.level_up)
        if level_up:
            self.apply_choice(game_data.menu_data.currchoice, game_data)
            game_data.player.caster.set_formulas(game_data.formula_builder.evaluate())
            self.choices = []
            return self.close(game_data, next_window=FormulaWindow)

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(Event.scroll_up)
        if scroll_up:
            self.prev_choice(game_data)
        scroll_down = mouse_action.get(Event.scroll_down)
        if scroll_down:
            self.next_choice(game_data)
