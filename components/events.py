from enum import Enum, auto

import attrdict
import pygame

from util import Pos


class EventType:
    move = "move"
    fullscreen = "fullscreen"
    exit = "exit"
    left_click = "left_click"
    right_click = "right_click"
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"
    level_up = "level_up"
    character_screen = "character_screen"
    formula_screen = "formula"
    start_throwing_vial = "start_throwing_vial"
    show_help = "show_help"
    interact = "interact"
    show_window = "show_window"
    keep_playing = "keep_playing"


class InputType(Enum):
    KEY = auto()
    MOUSE = auto()


class Event:
    def __init__(self, event_type, raw_event):
        self.event_type = event_type
        if raw_event:
            self.data = self.parse_raw(raw_event)
        else:
            self.data = None


class KeyEvent(Event):
    def __init__(self, raw_event):
        super(KeyEvent, self).__init__(InputType.KEY, raw_event)

    def parse_raw(self, raw_event):
        return attrdict.AttrDict({"key": raw_event.key})

    def serialize(self):
        return {"type": InputType.KEY.name,
                "key": self.data.key}

    @property
    def key(self):
        return self.data.key

    @staticmethod
    def deserialize(data):
        retr = KeyEvent(raw_event=None)
        retr.event_type = InputType.KEY
        retr.data = attrdict.AttrDict({"key": data["key"]})
        return retr


class MouseEvent(Event):
    def __init__(self, raw_event):
        super(MouseEvent, self).__init__(InputType.MOUSE, raw_event)

    def parse_raw(self, raw_event):
        mouse_pos = Pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        return attrdict.AttrDict({"type": InputType.MOUSE.name,
                                  "pos": mouse_pos,
                                  "button": raw_event.button})

    def serialize(self):
        return {"pos": (self.data.pos.x, self.data.pos.y),
                "button": self.data.button}

    @property
    def button(self):
        return self.data.button

    @staticmethod
    def deserialize(data):
        retr = MouseEvent(raw_event=None)
        retr.event_type = InputType.MOUSE
        retr.data = attrdict.AttrDict({"pos": Pos(data["pos"]["x"], data["pos"]["y"]),
                                       "button": data["button"]})
        return retr