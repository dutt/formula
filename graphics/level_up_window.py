import pygame

from graphics.display_helpers import display_text, display_lines
from graphics.window import Window
from input_handlers import Event


class LevelUpWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)

    def draw(self, game_data, gfx_data):
        if not self.visible:
            return False
        surface = pygame.Surface(self.size.tuple())
        header = [
            "You have expanded your skills and equipment, please choose:",
            ""
        ]
        linediff = 15
        y = 3 * linediff
        display_lines(surface, gfx_data.assets.font_message, header, starty=y)

        y += 2 * linediff
        choices = [
            "Bigger vials (+1 slot per vial)",
            "More vials (+1 prepared formula)"
        ]
        for idx, choice in enumerate(choices):
            text = choice
            if idx == game_data.menu_data.currchoice:
                text += "<--"
            display_text(surface, text, gfx_data.assets.font_message, (50, y))
            y += linediff
        gfx_data.main.blit(surface, self.pos.tuple())

        return True

    def handle_key(self, game_data, gfx_data, key_action):
        choice = key_action.get("choice")
        if choice:
            game_data.menu_data.currchoice += choice

        level_up = key_action.get(Event.level_up)
        if level_up:
            if game_data.menu_data.currchoice == 0:
                game_data.formula_builder.add_slot()
            elif game_data.menu_data.currchoice == 1:
                game_data.formula_builder.add_formula()
            self.close(game_data)
