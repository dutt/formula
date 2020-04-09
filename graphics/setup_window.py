import pygame

from graphics.display_helpers import display_text

# from graphics.minor_windows import WelcomeWindow
from graphics.window import Window
from systems.input_handlers import EventType


class SetupWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)

    def draw(self, game_data, gfx_data):
        if game_data.run_planner.gen_level_idx >= game_data.run_planner.level_count:
            # return self.close(game_data, WelcomeWindow)
            return self.close(game_data, None)

        surface = pygame.Surface(self.size.tuple())

        display_text(
            surface,
            "Generating level {}/{}".format(
                game_data.run_planner.gen_level_idx + 1, game_data.run_planner.level_count,
            ),
            gfx_data.assets.font_title,
            (50, 200),
        )
        gfx_data.main.blit(surface, self.pos.tuple())

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(EventType.exit)
        if do_quit:
            # return self.close(game_data, WelcomeWindow)
            return self.close(game_data, None)
