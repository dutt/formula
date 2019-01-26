import pygame

from graphics.window import TextWindow, Window
from util import resource_path
from graphics.display_helpers import display_text
from events import Event


class GeneralHelpWindow(TextWindow):
    PATH = resource_path("data/help/general.txt")

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, path=GeneralHelpWindow.PATH, next_window=None)


class AskQuitWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())
        display_text(surface, "Press Escape again to quit, press Space to keep playing",
                     gfx_data.assets.font_message, (150, 250))
        gfx_data.main.blit(surface, self.pos.tuple())

    def handle_key(self, game_data, gfx_data, key_action):
        keep_playing = key_action.get(Event.keep_playing)
        if keep_playing:
            self.close(game_data)

        do_exit = key_action.get(Event.exit)
        if do_exit:
            return None # propagate quit event
