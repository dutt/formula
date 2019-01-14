import pygame

from graphics.assets import Assets
from graphics.constants import colors
from graphics.display_helpers import display_text
from graphics.window import Window
from input_handlers import Event
from util import Pos


class MessageLogWindow(Window):
    def __init__(self, constants, parent):
        super().__init__(Pos(constants.right_panel_size.width, constants.game_window_size.height),
                         constants.message_log_size, visible=False, parent=parent)
        self.offset = 0
        self.num_messages = 9

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(game_data.constants.message_log_size.tuple())
        surface.fill(colors.BACKGROUND)
        messages = game_data.log.messages
        y = 0
        start = max(0, min(len(messages) - self.num_messages, len(messages) - self.num_messages + self.offset))
        end = min(len(messages), start + self.num_messages)
        for idx, msg in enumerate(messages[start:end]):
            display_text(surface, msg.text, Assets.get().font_message, (180, y + idx * 20), msg.color)
        gfx_data.main.blit(surface, self.pos.tuple())

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(Event.scroll_up)
        if scroll_up:
            self.offset = max(-len(game_data.log.messages) + self.num_messages, self.offset - 2)
        scroll_down = mouse_action.get(Event.scroll_down)
        if scroll_down:
            self.offset = min(len(game_data.log.messages) - self.num_messages, self.offset + 2)
