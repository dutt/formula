from graphics.assets import Assets
from graphics.display_helpers import display_text, display_bar, display_menu
from input_handlers import Event
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
    def __init__(self, pos, size, visible):
        super().__init__(pos, size)
        self.visible = visible

    def draw(self, game_data, gfx_data):
        raise NotImplementedError("draw called on Window base class")

    def close(self, game_data, next_window=None):
        game_data.state = game_data.prev_state.pop()
        self.visible = False
        return {Event.show_window: next_window}


class Bar(Clickable):
    def __init__(self, pos, color, bgcolor, size=Size(100, 30)):
        super().__init__(pos, size)
        self.color = color
        self.bgcolor = bgcolor

    def draw(self, surface, current_value, max_value):
        display_bar(surface, Assets.get(), self.pos, self.size.width, current_value,
                    max_value,
                    self.color, self.bgcolor)


class Label(Widget):
    def __init__(self, pos, text):
        super().__init__(pos, Size(0, 0))
        self.text = text

    def draw(self, surface):
        display_text(surface, self.text, Assets.get().font_title, self.pos.tuple())


class TextWindow(Window):
    def __init__(self, constants, visible, lines, next_window):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.lines = lines
        self.next_window = next_window

    def draw(self, game_data, gfx_data):
        if not self.visible:
            return False
        display_menu(gfx_data, self.lines, self.size.tuple())
        return True

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(Event.exit)
        if do_quit:
            return self.close(game_data, self.next_window)
