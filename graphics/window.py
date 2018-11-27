import pygame

from graphics.constants import colors
from graphics.display_helpers import display_text, display_bar
from util import Pos


class Window:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

    def is_clicked(self, pos):
        x_inside = self.pos.x <= pos.x <= (self.pos.x + self.size.width)
        y_inside = self.pos.y <= pos.y <= (self.pos.y + self.size.height)
        return x_inside and y_inside

    def handle_click(self, game_data, gfx_data, mouse_action):
        raise NotImplementedError("handle_click called on Window base class")

    def handle_key(self, key_action):
        raise NotImplementedError("handle_key called on Window base class")

    def draw(self, game_data, gfx_data):
        raise NotImplementedError("draw called on Window base class")


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
        return None

    def draw(self, game_data, gfx_data):
        for wnd in self.windows:
            wnd.draw(game_data, gfx_data)


class RightPanelWindow(Window):
    def __init__(self, constants):
        super(RightPanelWindow, self).__init__(Pos(0, 0), constants.right_panel_size)

    def handle_click(self, game_data, gfx_data, mouse_action):
        print("right panel clicked")
        
        return []

    def handle_key(self, key_action):
        print("right panel key")
        pass

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface((game_data.constants.right_panel_size.width, game_data.constants.window_size.height))
        surface.fill(game_data.constants.colors.dark_wall)
        assets = gfx_data.assets

        y = 20
        display_bar(surface, assets, Pos(10, y), 100, game_data.player.fighter.hp, game_data.player.fighter.max_hp,
                    (160, 0, 0), (100, 0, 0))

        if game_data.player.fighter.shield:
            y += 30
            display_bar(surface, assets, Pos(10, y), 100, game_data.player.fighter.shield.level,
                        game_data.player.fighter.shield.max_level,
                        (0, 160, 0), (0, 100, 0))

        y += 50
        display_text(surface, "Formulas", assets.font_title, (10, y))
        player = game_data.player
        y += 30
        for idx, formula in enumerate(player.caster.formulas):
            if player.caster.is_on_cooldown(idx):
                display_bar(surface, assets, Pos(20, y + idx * 20), 80, player.caster.get_cooldown(idx),
                            formula.cooldown,
                            (0, 127, 255), colors.BLACK)

            else:
                msg = "{}: {}".format(idx + 1, formula.text_repr)
                display_text(surface, msg, assets.font_message, (10, y + idx * 20))
            y += 40

        gfx_data.main.blit(surface, (0, 0))
