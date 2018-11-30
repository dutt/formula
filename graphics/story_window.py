import textwrap

import pygame

from graphics.display_helpers import display_text, display_menu
from graphics.formula_window import FormulaWindow
from graphics.window import Window, TextWindow
from input_handlers import Event


class StoryHelpWindow(TextWindow):
    LINES = [
        "This is the next page of the story",
        "",
        "Press Space for the next page",
        "Press Escape or Tab to go back",
    ]

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, StoryHelpWindow.LINES, None)


class StoryWindow(Window):
    def __init__(self, constants, visible=False, story_data=None):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.story_data = story_data

    def draw(self, game_data, gfx_data):
        if not self.visible:
            return False
        surface = pygame.Surface(self.size.tuple())
        page_lines = self.story_data.current_page.split("\n")
        lines = []
        for pl in page_lines:
            if pl == "":
                lines.append("")
            else:
                lines.extend(textwrap.wrap(pl, 60))
        display_menu(gfx_data, lines, (800, 600), surface=surface)
        display_text(surface, "{}/{}".format(self.story_data.page_num, self.story_data.page_count),
                     gfx_data.assets.font_message, (40, 400))
        gfx_data.main.blit(surface, self.pos.tuple())
        return True

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(Event.exit)
        if do_quit:
            return self.close(game_data, FormulaWindow)

        next = key_action.get("next")
        if next:
            if game_data.story.is_last_page:
                return self.close(game_data, FormulaWindow)
            else:
                game_data.story.next_page()
                return {}
