import textwrap

import pygame

from graphics.display_helpers import display_text, display_lines
from graphics.window import Window, TextWindow
from input_handlers import Event


class FormulaHelpWindow(TextWindow):
    LINES = [
        "Building formulas:",
        "Q,W,E,R,A,S, D: Set current slot to ingredient",
        "Up/down arrow: Switch to next/previous slot",
        "Right/left arrow: Switch to next/previous formula",
        "Cooldown is increased for every used slot",
        "",
        "Q: Empty, clear the slot",
        "W: Fire, increases damage",
        "E: Range, vial can be thrown further",
        "R: Area, wider area of effect",
        "A: Cold, less damage than fire, but also slows the enemy",
        "S: Life, heal the target",
        "D: Shield, resists damage. Combine with others for strikebacks",
        "    3*Shield = 12 dmg resisted",
        "    2*Shield + Fire = 8 dmg resisted, 1 fire hit back when you're hit",
        "    Shield + Fire + Range, 4 dmg, hit back also when hit from short range",
        "",
        "If this is your first run I recommend 3*Fire, 2*Fire+Range, 3*Shield",
        "",
        "Tab: Close this help"
    ]

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, FormulaHelpWindow.LINES, None)


class FormulaWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())
        linediff = 12
        y = 5 * linediff
        display_text(surface, "Formulas", gfx_data.assets.font_message, (50, y))

        y += 2 * linediff
        display_text(surface, "Vial slots:", gfx_data.assets.font_message, (50, y))
        y += linediff
        for idx, formula in enumerate(game_data.formula_builder.current_slots):
            text = "Slot {}: {}".format(idx, formula.name)
            if idx == game_data.formula_builder.currslot:
                text += "<-- "
            display_text(surface, text, gfx_data.assets.font_message, (50, y))
            y += linediff

        y += 3 * linediff
        display_text(surface, "Formula {}".format(game_data.formula_builder.currformula + 1),
                     gfx_data.assets.font_message,
                     (50, y))

        formulas = game_data.formula_builder.evaluate()

        y += linediff
        display_text(surface, "Formula stats:", gfx_data.assets.font_message, (50, y))

        y += linediff * 2
        cooldown_text = "Cooldown: {} rounds".format(formulas[game_data.formula_builder.currformula].cooldown)
        display_text(surface, cooldown_text, gfx_data.assets.font_message, (50, y))

        y += linediff * 2
        lines = textwrap.wrap(formulas[game_data.formula_builder.currformula].text_stats, 60)
        display_lines(surface, gfx_data.assets.font_message, lines, 50, y, ydiff=10)
        y += len(lines) * linediff

        y += 6 * linediff
        display_text(surface, "Arrow left/right or Mouse left/right: select formula",
                     gfx_data.assets.font_message,
                     (50, y))
        y += linediff
        display_text(surface, "Arrow up/down or Mouse scroll: select slot",
                     gfx_data.assets.font_message,
                     (50, y))
        y += 2* linediff
        display_text(surface, "Press Tab for help, or Space to confirm selection",
                     gfx_data.assets.font_message,
                     (50, y))
        ingredient_lines = [
            "Q: Empty",
            "W: Fire",
            "E: Range",
            "R: Area",
            "A: Cold",
            "S: Life",
            "D: Shield"
        ]
        display_lines(surface, gfx_data.assets.font_message, ingredient_lines, 400, 65, ydiff=12)

        gfx_data.main.blit(surface, self.pos.tuple())

    def change_slot(self, game_data, pos_diff):
        next_num = (game_data.formula_builder.currslot + pos_diff) % game_data.formula_builder.num_slots
        game_data.formula_builder.currslot = next_num

    def change_formula(self, game_data, pos_diff):
        next_num = (game_data.formula_builder.currformula + pos_diff) % game_data.formula_builder.num_formula
        game_data.formula_builder.currformula = next_num
        # go to first slot
        game_data.formula_builder.currslot = 0

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(Event.exit)
        if do_quit:
            #
            #game_data.state = game_data.prev_state.pop()
            #self.visible = False
            game_data.player.caster.set_formulas(game_data.formula_builder.evaluate())
            gfx_data.camera.initialize_map()
            gfx_data.camera.center_on(game_data.player.pos.x, game_data.player.pos.y)
            #return {}
            from graphics.game_window import GameWindow
            return self.close(game_data, GameWindow)

        slot = key_action.get("slot")
        if slot is not None:
            game_data.formula_builder.currslot = slot
            return {}

        ingredient = key_action.get("ingredient")
        if ingredient:
            game_data.formula_builder.set_slot(game_data.formula_builder.currslot, ingredient)
            self.change_slot(game_data, 1)
            return {}

        next_formula = key_action.get("next_formula")
        if next_formula:
            self.change_formula(game_data, 1)
            return {}

        next_slot = key_action.get("next_slot")
        if next_slot:
            self.change_slot(game_data, 1)
            return {}

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(Event.scroll_up)
        if scroll_up:
            self.change_slot(game_data, -1)

        scroll_down = mouse_action.get(Event.scroll_down)
        if scroll_down:
            self.change_slot(game_data, 1)

        right_clicked = mouse_action.get(Event.right_click)
        if right_clicked:
            self.change_formula(game_data, 1)

        left_clicked = mouse_action.get(Event.left_click)
        if left_clicked:
            self.change_formula(game_data, -1)
