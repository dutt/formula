import textwrap

import pygame

from graphics.assets import Assets
from graphics.display_helpers import display_text, display_bar, display_menu
from graphics.constants import colors
from systems.input_handlers import EventType
from util import Size


class Widget:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size


class Clickable(Widget):
    def is_clicked(self, mouse_action):
        val = list(mouse_action.values())[0]
        x, y = val.x, val.y
        x_inside = self.pos.x <= x <= (self.pos.x + self.size.width)
        y_inside = self.pos.y <= y <= (self.pos.y + self.size.height)
        return x_inside and y_inside

    def handle_click(self, game_data, gfx_data, mouse_action):
        pass

    def handle_key(self, game_data, gfx_data, key_action):
        pass


class Window(Clickable):
    def __init__(self, pos, size, visible, parent=None):
        super().__init__(pos, size)
        self._visible = visible
        self.children = []
        self.parent = parent
        if parent:
            parent.children.append(self)

    def draw(self, game_data, gfx_data):
        raise NotImplementedError("draw called on Window base class")

    def close(self, game_data, next_window=None):
        game_data.state = game_data.prev_state.pop()
        self.visible = False
        return {EventType.show_window: next_window}

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        for child in self.children:
            child.visible = value


class Bar(Clickable):
    def __init__(self, pos, text=None, color=colors.WHITE, bgcolor=colors.BACKGROUND, size=Size(100, 30), show_numbers=True):
        super().__init__(pos, size)
        self.color = color
        self.text = text
        self.bgcolor = bgcolor
        self.show_numbers = show_numbers

    def draw(self, surface, current_value, max_value):
        display_bar(surface, Assets.get(), self.pos, self.size.width, current_value, max_value,
                    self.color, self.bgcolor, text = self.text, show_numbers=self.show_numbers)


class Label(Widget):
    def __init__(self, pos, text):
        super().__init__(pos, Size(0, 0))
        self.text = text

    def draw(self, surface):
        display_text(surface, self.text, Assets.get().font_title, self.pos.tuple())


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
        with open(path, 'r') as reader:
            return reader.read().split("\n")

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

        if len(all_lines) > self.num_lines:
            display_text(surface, "Use W, S or mouse scroll to see more", gfx_data.assets.font_message, (50, 500))

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
            return self.close(game_data, self.next_window)

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

