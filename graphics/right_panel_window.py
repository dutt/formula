import pygame

from graphics.assets import Assets
from graphics.constants import colors
from graphics.display_helpers import display_text
from graphics.window import Window, Bar, Label, Clickable
from input_handlers import Event
from util import Pos, Size


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


class RightPanelWindow(Window):
    def __init__(self, constants):
        super().__init__(Pos(0, 0), constants.right_panel_size, visible=True)
        self.health_bar = Bar(Pos(10, 20), colors.HP_BAR_FRONT, colors.HP_BAR_BACKGROUND)
        self.shield_bar = Bar(Pos(10, 60), colors.SHIELD_BAR_FRONT, colors.SHIELD_BAR_BACKGROUND)
        self.formula_label = Label(Pos(10, 150), "Formulas")
        self.formula_markers = []

    def handle_click(self, game_data, gfx_data, mouse_action):
        for fm in self.formula_markers:
            if fm.is_clicked(mouse_action):
                return fm.handle_click(game_data, gfx_data, mouse_action)
        return {}

    def handle_key(self, game_data, gfx_data, key_action):
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
            self.update_formula_markers(game_data.player, start_y=self.formula_label.pos.y + 40)

        self.health_bar.draw(surface, game_data.player.fighter.hp, game_data.player.fighter.max_hp)
        if game_data.player.fighter.shield:
            self.shield_bar.draw(surface, game_data.player.fighter.shield.level,
                                 game_data.player.fighter.shield.max_level)

        self.formula_label.draw(surface)
        for idx, fm in enumerate(self.formula_markers):
            fm.draw(surface, game_data.player.caster.formulas[idx])

        gfx_data.main.blit(surface, self.pos.tuple())
        return True
