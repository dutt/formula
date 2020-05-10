from enum import Enum, auto
import json

import attrdict
import pygame

from util import Pos
from systems.blob_logger import BlobLogger

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
    activate_for_new_state = "activate_for_new_state"
    console = "console"
    start_crafting = "start_crafting"
    use_consumable = "use_consumable"
    inventory = "inventory"


class InputType(Enum):
    KEY = auto()
    MOUSE = auto()


class Event:
    def __init__(self, event_type, raw_event):
        self.event_type = event_type
        self.event_id = BlobLogger.get().allocate_id()
        if raw_event:
            self.data = self.parse_raw(raw_event)
        else:
            self.data = None

    def serialize(self):
        return { "event_id" : self.event_id }

    def deserialize(self, data):
        self.event_id = data["event_id"]


class KeyEvent(Event):
    def __init__(self, raw_event):
        super().__init__(InputType.KEY, raw_event)

    def parse_raw(self, raw_event):
        return attrdict.AttrDict({"key": raw_event.key })

    def serialize(self):
        retr = super().serialize()
        retr.update({
            "type": InputType.KEY.name,
            "key": self.data.key})
        return retr

    @property
    def key(self):
        return self.data.key

    @staticmethod
    def deserialize(data):
        retr = KeyEvent(raw_event=None)
        retr.deserialize(data)
        retr.event_type = InputType.KEY
        retr.data = attrdict.AttrDict(data)
        return retr

    def __str__(self):
        return f"<KeyEvent key={self.key}>"

    def __repr__(self):
        return str(self)


class MouseEvent(Event):
    def __init__(self, raw_event):
        super().__init__(InputType.MOUSE, raw_event)

    def parse_raw(self, raw_event):
        mouse_pos = Pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        return attrdict.AttrDict({"type": InputType.MOUSE.name,
                                  "x": mouse_pos.x, "y" : mouse_pos.y,
                                  "button": raw_event.button})

    def serialize(self):
        retr = super().serialize()
        retr.update({
            "type": InputType.MOUSE.name,
        })
        for key, value in self.data.items():
            retr[key] = value
        return retr

    @property
    def button(self):
        return self.data.button

    @property
    def pos(self):
        return Pos(self.data.x, self.data.y)

    @staticmethod
    def deserialize(data):
        retr = MouseEvent(raw_event=None)
        retr.deserialize(data)
        retr.event_type = InputType.MOUSE
        retr.data = attrdict.AttrDict(data)
        return retr

    def __str__(self):
        return f"<MouseEvent pos={self.pos} button={self.button}>"

    def __repr__(self):
        return str(self)
