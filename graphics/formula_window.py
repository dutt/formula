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
        "Adding fire to a formula increases damage",
        "Adding life to a formula increases healing",
        "Adding range to a formula makes it reach further",
        "Adding area to a formula gives it wider area of effect",
        "Adding shield makes it defensive, combine with others for a shield that strikes back on hits",
        "Adding cold does less damage than fire, but also slows the enemy down"
    ]

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, FormulaHelpWindow.LINES, None)


class FormulaWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)

    def draw(self, game_data, gfx_data):
        if not self.visible:
            return False

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
        display_text(surface,
                     "Formula stats:",
                     gfx_data.assets.font_message,
                     (50, y))
        y += linediff
        lines = textwrap.wrap(formulas[game_data.formula_builder.currformula].text_stats, 60)
        display_lines(surface, gfx_data.assets.font_message, lines, 50, y, ydiff=10)
        y += len(lines) * linediff

        y += 6 * linediff
        display_text(surface, "Press Tab for help".format(game_data.formula_builder.currformula + 1),
                     gfx_data.assets.font_message,
                     (50, y))
        gfx_data.main.blit(surface, self.pos.tuple())
        return True

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(Event.exit)
        if do_quit:
            # return self.close(game_data, FormulaWindow)
            game_data.state = game_data.prev_state.pop()
            self.visible = False
            game_data.player.caster.set_formulas(game_data.formula_builder.evaluate())
            gfx_data.camera.center_on(game_data.player.pos.x, game_data.player.pos.y)
            return {}

        slot = key_action.get("slot")
        if slot is not None:
            game_data.formula_builder.currslot = slot
            return {}

        ingredient = key_action.get("ingredient")
        if ingredient:
            game_data.formula_builder.set_slot(game_data.formula_builder.currslot, ingredient)
            # go to next slot
            next_num = (game_data.formula_builder.currslot + 1) % game_data.formula_builder.num_slots
            game_data.formula_builder.currslot = next_num
            return {}

        next_formula = key_action.get("next_formula")
        if next_formula:
            next_num = (game_data.formula_builder.currformula + next_formula) % game_data.formula_builder.num_formula
            game_data.formula_builder.currformula = next_num
            # go to first slot
            game_data.formula_builder.currslot = 0
            return {}

        next_slot = key_action.get("next_slot")
        if next_slot:
            next_num = (game_data.formula_builder.currslot + next_slot) % game_data.formula_builder.num_slots
            game_data.formula_builder.currslot = next_num
            return {}
