import pygame

from graphics.assets import Assets
from graphics.constants import colors
from graphics.display_helpers import display_text, display_bar
from input_handlers import Event
from util import Pos, Size


class WindowManager:
    def __init__(self):
        self.windows = []

    def push(self, window):
        self.windows.append(window)

    def pop(self):
        self.windows.pop()

    def remove(self, window):
        self.windows.remove(window)

    def handle_click(self, game_data, gfx_data, mouse_action):
        for wnd in reversed(self.windows):
            if wnd.is_clicked(mouse_action):
                return wnd.handle_click(game_data, gfx_data, mouse_action)
        return {}

    def draw(self, game_data, gfx_data):
        for wnd in self.windows:
            wnd.draw(game_data, gfx_data)


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
        raise NotImplementedError("handle_click called on Window base class")

    def handle_key(self, key_action):
        raise NotImplementedError("handle_key called on Window base class")


class Window(Clickable):
    def __init__(self, pos, size):
        super().__init__(pos, size)

    def draw(self, game_data, gfx_data):
        raise NotImplementedError("draw called on Window base class")


class Bar(Clickable):
    def __init__(self, pos, color, bgcolor, size=Size(100, 30)):
        super().__init__(pos, size)
        self.color = color
        self.bgcolor = bgcolor

    def draw(self, surface, current_value, max_value):
        display_bar(surface, Assets.get(), self.pos, self.size.width, current_value,
                    max_value,
                    self.color, self.bgcolor)


class FormulaMarker(Clickable):
    def __init__(self, pos, formula_idx, player, size=Size(100, 30)):
        super().__init__(pos, size)
        self.formula_idx = formula_idx
        self.player = player
        self.cooldown_bar = Bar(pos, colors.COOLDOWN_BAR_FRONT, colors.COOLDOWN_BAR_BACKGROUND)

    def draw(self, surface, formula):
        if self.player.caster.is_on_cooldown(self.formula_idx):
            self.cooldown_bar.draw(surface, self.player.caster.get_cooldown(self.formula_idx), formula.cooldown)
        else:
            msg = "{}: {}".format(self.formula_idx + 1, formula.text_repr)
            display_text(surface, msg, Assets.get().font_message, self.pos.tuple())

    def handle_click(self, game_data, gfx_data, mouse_action):
        left_click = mouse_action.get(Event.left_click)
        if left_click:
            print("Formula {} clicked".format(self.formula_idx))
            return {Event.start_throwing_vial: self.formula_idx}


class Label(Widget):
    def __init__(self, pos, text):
        super().__init__(pos, Size(0, 0))
        self.text = text

    def draw(self, surface):
        display_text(surface, self.text, Assets.get().font_title, self.pos.tuple())


class RightPanelWindow(Window):
    def __init__(self, constants):
        super().__init__(Pos(0, 0), constants.right_panel_size)
        self.health_bar = Bar(Pos(10, 20), colors.HP_BAR_FRONT, colors.HP_BAR_BACKGROUND)
        self.shield_bar = Bar(Pos(10, 50), colors.SHIELD_BAR_FRONT, colors.SHIELD_BAR_BACKGROUND)
        self.formula_label = Label(Pos(10, 70), "Formulas")
        self.formula_markers = []

    def handle_click(self, game_data, gfx_data, mouse_action):
        for fm in self.formula_markers:
            if fm.is_clicked(mouse_action):
                return fm.handle_click(game_data, gfx_data, mouse_action)
        return {}

    def handle_key(self, key_action):
        print("right panel key")

    def update_formula_markers(self, player, start_y):
        y = start_y
        for idx, formula in enumerate(player.caster.formulas):
            marker = FormulaMarker(Pos(20, y), idx, player)
            self.formula_markers.append(marker)
            y += 40

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(game_data.constants.right_panel_size.tuple())
        surface.fill(colors.BACKGROUND)

        if len(self.formula_markers) != len(game_data.player.caster.formulas):
            self.update_formula_markers(game_data.player, start_y=100)

        self.health_bar.draw(surface, game_data.player.fighter.hp, game_data.player.fighter.max_hp)
        if game_data.player.fighter.shield:
            self.shield_bar.draw(surface, game_data.player.fighter.shield.level, game_data.player.fighter.max_level)

        self.formula_label.draw(surface)
        for idx, fm in enumerate(self.formula_markers):
            fm.draw(surface, game_data.player.caster.formulas[idx])

        gfx_data.main.blit(surface, self.pos.tuple())


class MessageLogWindow(Window):
    def __init__(self, constants):
        super().__init__(Pos(constants.right_panel_size.width, constants.game_window_size.height),
                         constants.message_log_size)
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
            self.offset -= 2
        scroll_down = mouse_action.get(Event.scroll_down)
        if scroll_down:
            self.offset += 2
