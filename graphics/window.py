from enum import Enum, auto
import textwrap

import pygame

from graphics.assets import Assets
from graphics.display_helpers import display_text, display_bar
from graphics.constants import colors
from systems.input_handlers import EventType
from util import Size


class Widget:
    def __init__(self, pos, size, parent):
        self.pos = pos
        self.size = size
        self.parent = parent


class ClickMode(Enum):
    LEFT = auto()
    RIGHT = auto()
    SCROLL = auto()

class Clickable(Widget):
    def __init__(self, pos, size, parent=None, click_mode=None):
        super().__init__(pos, size, parent)
        self.click_mode = click_mode

    def is_inside(self, x, y):
        x_inside = self.pos.x <= x <= (self.pos.x + self.size.width)
        y_inside = self.pos.y <= y <= (self.pos.y + self.size.height)
        return x_inside and y_inside

    def is_clicked(self, mouse_action):
        if not self.click_mode:
            return False
        if self.click_mode == ClickMode.LEFT:
            if "left_click" in mouse_action:
                val = mouse_action["left_click"]
            else:
                return False
        elif self.click_mode == ClickMode.RIGHT:
            if "right_click" in mouse_action:
                val = mouse_action["right_click"]
            else:
                return False
        elif self.click_mode == ClickMode.SCROLL:
            if "scroll_up" in mouse_action:
                val = mouse_action["scroll_up"]
            elif "scroll_down" in mouse_action:
                val = mouse_action["scroll_down"]
            else:
                return False

        x, y = val.x, val.y
        if self.parent:
            x -= self.parent.pos.x
            y -= self.parent.pos.y
        return self.is_inside(x, y)

    def handle_click(self, game_data, gfx_data, mouse_action):
        pass

    def handle_key(self, game_data, gfx_data, key_action):
        pass


class Window(Clickable):
    def __init__(self, pos, size, visible, parent=None, click_mode=None):
        super().__init__(pos, size, parent, click_mode=click_mode)
        self._visible = visible
        self.children = []
        self.drawing_priority = 1
        if parent:
            parent.children.append(self)

    def draw(self, game_data, gfx_data):
        raise NotImplementedError("draw called on Window base class")

    # Called when the window is displayed
    def init(self, game_data, gfx_data):
        pass

    def close(self, game_data, next_window=None, activate_for_new_state=False):
        game_data.state = game_data.prev_state.pop()
        self.visible = False
        return {
            EventType.show_window: next_window,
            EventType.activate_for_new_state: activate_for_new_state,
        }

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        for child in self.children:
            child.visible = value


class Bar(Clickable):
    def __init__(
        self, pos, text=None, color=colors.WHITE, bgcolor=colors.BACKGROUND, size=Size(100, 30), show_numbers=True,
    ):
        super().__init__(pos, size)
        self.color = color
        self.text = text
        self.bgcolor = bgcolor
        self.show_numbers = show_numbers

    def draw(self, surface, current_value, max_value):
        display_bar(
            surface,
            Assets.get(),
            self.pos,
            self.size.width,
            current_value,
            max_value,
            self.color,
            self.bgcolor,
            text=self.text,
            show_numbers=self.show_numbers,
        )


class Label(Widget):
    def __init__(self, pos, text, font=None, parent=None):
        super().__init__(pos, Size(0, 0), parent=parent)
        self.text = text
        self.font = font if font else Assets.get().font_title

    def draw(self, surface):
        display_text(surface, self.text, self.font, self.pos.tuple())

class ClickableLabel(Clickable):
    def __init__(self, pos, text, size, font=None, parent=None):
        super().__init__(pos, size, parent=parent)
        self.text = text
        self.font = font if font else Assets.get().font_title

    def draw(self, surface):
        display_text(surface, self.text, self.font, self.pos.tuple())
