import textwrap

import pygame

from graphics.display_helpers import display_text, display_menu
from graphics.window import Window
from components.events import EventType


class TextWindow(Window):
    def __init__(self, constants, visible, lines=None, path=None, next_window=None):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.next_window = next_window
        self.lines = lines
        self.num_lines = 20
        self.offset = 0
        self.offset_jump = 1
        self.path = path
        assert path or lines
        if path:
            self.lines = self.load_path(path)

    def load_path(self, path):
        with open(path, "r") as reader:
            lines = reader.read().split("\n")
            all_lines = []
            for current in lines:
                if current.strip() == "":
                    all_lines.append(current)
                else:
                    split_lines = textwrap.wrap(current, 60)
                    all_lines.extend(split_lines)
            return all_lines

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())

        show_lines = self.lines[self.offset : self.offset + self.num_lines]
        display_menu(gfx_data, show_lines, self.size.tuple(), surface=surface, x=self.pos.x + 10)

        if len(self.lines) > self.num_lines:
            pygame.draw.line(surface, (255, 255, 255), (100, 520), (500, 520))
            display_text(
                surface, "Use W, S or mouse scroll to see more", gfx_data.assets.font_message, (130, 530),
            )

        gfx_data.main.blit(surface, self.pos.tuple())

    def scroll_up(self):
        if self.num_lines > len(self.lines):
            self.offset = max(self.offset - self.offset_jump, 0)
        else:
            self.offset = max(-len(self.lines) + self.num_lines, self.offset - self.offset_jump, 0)

    def scroll_down(self):
        if self.num_lines > len(self.lines):
            self.offset = min(self.offset + self.offset_jump, len(self.lines))
        else:
            self.offset = min(len(self.lines) - self.num_lines, self.offset + self.offset_jump)

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(EventType.exit)
        if do_quit:
            return self.close(game_data)

        scroll_up = key_action.get(EventType.scroll_up)
        if scroll_up:
            self.scroll_up()

        scroll_down = key_action.get(EventType.scroll_down)
        if scroll_down:
            self.scroll_down()

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(EventType.scroll_up)
        if scroll_up:
            self.scroll_up()

        scroll_down = mouse_action.get(EventType.scroll_down)
        if scroll_down:
            self.scroll_down()
