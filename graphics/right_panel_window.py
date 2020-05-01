import pygame

from graphics.assets import Assets
from graphics.constants import colors
from graphics.display_helpers import display_text
from graphics.window import Window, Bar, Label, Clickable, ClickMode
from systems.input_handlers import EventType
from util import Pos, Size
import config


class FormulaMarker(Clickable):
    def __init__(self, pos, formula_idx, player, size=Size(100, 30)):
        super().__init__(pos, size, click_mode=ClickMode.LEFT)
        self.formula_idx = formula_idx
        self.player = player
        self.cooldown_bar = Bar(
            pos, None, colors.COOLDOWN_BAR_FRONT, colors.COOLDOWN_BAR_BACKGROUND, show_numbers=False,
        )
        self.font = Assets.get().font_message

    def draw(self, surface, game_data, formula):
        if self.player.caster.is_on_cooldown(self.formula_idx):
            self.cooldown_bar.draw(
                surface, self.player.caster.get_cooldown(self.formula_idx), formula.cooldown,
            )
        elif self.formula_idx == game_data.targeting_formula_idx:
            msg = "{}: {}".format(self.formula_idx + 1, formula.text_repr)
            x, y = self.pos.x - 5, self.pos.y - 5
            w, h = self.size.width, self.size.height
            pygame.draw.rect(surface, (150, 75, 75), (x, y, w, h), 5)
            display_text(surface, msg, self.font, self.pos.tuple())
        else:
            msg = "{}: {}".format(self.formula_idx + 1, formula.text_repr)
            display_text(surface, msg, self.font, self.pos.tuple())

    def handle_click(self, game_data, gfx_data, mouse_action):
        left_click = mouse_action.get(EventType.left_click)
        if left_click:
            return {EventType.start_throwing_vial: self.formula_idx}

class ConsumableMarker(Clickable):
    def __init__(self, pos, consumable_index, size=Size(130, 30)):
        super().__init__(pos, size, click_mode=ClickMode.LEFT)
        self.consumable_index = consumable_index
        self.shortcut = self.get_shortcut(self.consumable_index)
        self.font = Assets.get().font_message

    def get_shortcut(self, consumable_index):
        if consumable_index == 0:
            return "Z"
        elif consumable_index == 1:
            return "X"
        elif consumable_index == 2:
            return "C"
        else:
            raise ValueError(f"Unknown consumable index {consumable_index}")

    def draw(self, surface, game_data, gfx_data):
        x, y = self.pos.tuple()
        w, h = self.size.tuple()
        pygame.draw.rect(surface, (100, 50, 50), (x,y,w,h), 1)
        item = game_data.inventory.get_quickslot(self.consumable_index)
        if item:
            display_text(surface, f"{self.shortcut}: {item.name}", self.font, self.pos.tuple())
        else:
            display_text(surface, f"{self.shortcut}: -", self.font, self.pos.tuple())

    def handle_click(self, game_data, gfx_data, mouse_action):
        print(f"consumable {self.consumable_index} clicked")
        left_click = mouse_action.get(EventType.left_click)
        if left_click and game_data.inventory.get_quickslot(self.consumable_index):
            return {EventType.use_consumable: self.consumable_index}


class RightPanelWindow(Window):
    def __init__(self, constants, parent=None):
        super().__init__(Pos(0, 0), constants.right_panel_size, visible=False, parent=parent, click_mode=ClickMode.LEFT)
        self.health_bar = Bar(Pos(10, 20), "HP", colors.HP_BAR_FRONT, colors.HP_BAR_BACKGROUND, size=Size(120, 30),)
        self.shield_bar = Bar(
            Pos(10, 60), "Shield", colors.SHIELD_BAR_FRONT, colors.SHIELD_BAR_BACKGROUND, size=Size(120, 30),
        )
        self.xp_bar = Bar(
            Pos(10, 130),
            text=None,
            color=colors.XP_BAR_FRONT,
            bgcolor=colors.XP_BAR_BACKGROUND,
            size=Size(120, 30),
            show_numbers=False,
        )
        self.formula_label = Label(Pos(10, 180), "Formulas")
        self.formula_markers = []
        self.setup_consumables(constants.num_quickslots)
        self.drawing_priority = 2

    def setup_consumables(self, count):
        self.consumable_markers = []
        y = 650
        for idx in range(count):
            pos = Pos(10, y)
            self.consumable_markers.append(ConsumableMarker(pos, idx))
            y += 40

    def handle_click(self, game_data, gfx_data, mouse_action):
        for fm in self.formula_markers:
            if fm.is_clicked(mouse_action):
                return fm.handle_click(game_data, gfx_data, mouse_action)

        if config.conf.consumables:
            for cm in self.consumable_markers:
                if cm.is_clicked(mouse_action):
                    return cm.handle_click(game_data, gfx_data, mouse_action)

        return {}

    def handle_key(self, game_data, gfx_data, key_action):
        pass

    def update_formula_markers(self, player, start_y):
        y = start_y
        self.formula_markers.clear()
        for idx, _ in enumerate(player.caster.formulas):
            marker = FormulaMarker(Pos(20, y), idx, player)
            self.formula_markers.append(marker)
            y += 40

    def draw_mouse_over_info(self, surface, game_data, gfx_data):
        mx, my = pygame.mouse.get_pos()
        if self.health_bar.is_inside(mx, my):
            display_text(surface, "This is how much health you have", Assets.get().font_message, (mx, my))
        elif self.shield_bar.is_inside(mx, my):
            display_text(surface, "This is how much shield you have", Assets.get().font_message, (mx, my))
        for fm in self.formula_markers:
            if fm.is_inside(mx, my):
                display_text(surface, "A formula", Assets.get().font_message, (mx, my))
                return
        for cm in self.consumable_markers:
            if cm.is_inside(mx, my):
                item = game_data.inventory.get_quickslot(cm.consumable_index)
                if item:
                    display_text(gfx_data.main, item.DESCRIPTION, Assets.get().font_message, (mx, my))
                else:
                    display_text(gfx_data.main, "No item equipped", Assets.get().font_message, (mx, my))
                return

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(game_data.constants.right_panel_size.tuple())
        surface.fill(colors.BACKGROUND)

        if len(self.formula_markers) != len(game_data.player.caster.formulas):
            self.update_formula_markers(game_data.player, start_y=self.formula_label.pos.y + 40)

        self.health_bar.draw(surface, game_data.player.fighter.hp, game_data.player.fighter.max_hp)
        if game_data.player.fighter.shield:
            self.shield_bar.draw(
                surface, game_data.player.fighter.shield.level, game_data.player.fighter.shield.max_level,
            )
        else:
            self.shield_bar.draw(
                surface, 0, 10
            )

        if config.conf.keys:
            if game_data.map.stairs_found:
                text = "Found {}/{} keys".format(game_data.map.num_keys_found, game_data.map.num_keys_total)
            else:
                text = "Found {}/? keys".format(game_data.map.num_keys_found)
            display_text(
                surface, text, Assets.get().font_message, (10, 105),
            )
        else:
            display_text(
                surface, "Level {}".format(game_data.player.level.current_level), Assets.get().font_message, (10, 105),
            )
            if config.conf.keys:
                self.xp_bar.draw(
                    surface, game_data.player.level.current_xp, game_data.player.level.xp_to_next_level,
                )

        self.formula_label.draw(surface)
        for idx, fm in enumerate(self.formula_markers):
            fm.draw(surface, game_data, game_data.player.caster.formulas[idx])

        if config.conf.consumables:
            for cm in self.consumable_markers:
                cm.draw(surface, game_data, gfx_data)

        display_text(
            surface,
            "Floor {}".format(game_data.run_planner.current_level_index + 1),
            Assets.get().font_message,
            (10, 850),
        )

        gfx_data.main.blit(surface, self.pos.tuple())

        self.draw_mouse_over_info(gfx_data.main, game_data, gfx_data)
