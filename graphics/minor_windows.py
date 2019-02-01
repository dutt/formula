import textwrap

import pygame

from events import Event
from graphics.display_helpers import display_text, display_lines, display_menu
from graphics.window import TextWindow, Window
from util import resource_path


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
            return None  # propagate quit event


class DeadWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())
        display_text(surface, "You died", gfx_data.assets.font_message, (300, 100))
        display_text(surface, "Killed by a {} after killing...".format(game_data.player.fighter.killed_by.name),
                     gfx_data.assets.font_message, (120, 150))

        kills = game_data.stats.monsters_per_type
        lines = []
        for k in kills:
            lines.append("{} {}".format(kills[k], k))
        display_lines(surface, gfx_data.assets.font_message, lines, x=120, starty=180, ydiff=14)

        display_text(surface, "Press Escape again to quit, press Space to keep playing",
                     gfx_data.assets.font_message, (120, 500))
        gfx_data.main.blit(surface, self.pos.tuple())

    def handle_key(self, game_data, gfx_data, key_action):
        keep_playing = key_action.get(Event.keep_playing)
        if keep_playing:
            return None  # propagate exit, restart

        do_exit = key_action.get(Event.exit)
        if do_exit:
            return None  # propagate quit event


class VictoryWindow(TextWindow):
    PATH = resource_path("data/story/floor.10.txt")

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, path=VictoryWindow.PATH, next_window=None)

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())

        all_lines = []
        for current in self.lines:
            if current.strip() == "":
                all_lines.append(current)
            else:
                split_lines = textwrap.wrap(current, 60)
                all_lines.extend(split_lines)
        show_lines = all_lines[self.offset:self.offset + self.num_lines]
        display_menu(gfx_data, show_lines, self.size.tuple(), surface=surface)

        display_text(surface, "Press Escape to quit, press Space to play again", gfx_data.assets.font_message, (150, 500))

        gfx_data.main.blit(surface, self.pos.tuple())

    def handle_key(self, game_data, gfx_data, key_action):
        keep_playing = key_action.get(Event.keep_playing)
        if keep_playing:
            return None  # propagate exit, restart

        do_exit = key_action.get(Event.exit)
        if do_exit:
            return None  # propagate quit event
