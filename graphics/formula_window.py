import textwrap

import pygame

from graphics.display_helpers import display_text, display_lines
from graphics.window import Window, TextWindow
from graphics.story_window import StoryWindow
from systems.input_handlers import EventType
from components.game_states import GameStates
from util import resource_path


class FormulaHelpWindow(TextWindow):
    PATH = resource_path("data/help/formula_window.txt")

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, path=FormulaHelpWindow.PATH, next_window=None)


class FormulaWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)

    def draw(self, game_data, gfx_data):
        def draw_ingredient_list():
            from components.ingredients import Ingredient
            ingredient_lines = [
                "Q: Empty"
            ]
            if game_data.formula_builder.ingredient_unlocked(Ingredient.FIRE):
                if game_data.formula_builder.ingredient_unlocked(Ingredient.INFERNO):
                    ingredient_lines.append("W: Inferno")
                elif game_data.formula_builder.ingredient_unlocked(Ingredient.FIREBOLT):
                    ingredient_lines.append("W: Firebolt")
                elif game_data.formula_builder.ingredient_unlocked(Ingredient.FIRESPRAY):
                    ingredient_lines.append("W: Firespray")
                else:
                    ingredient_lines.append("W: Fire")
            ingredient_lines.extend([
                "E: Range" if game_data.formula_builder.ingredient_unlocked(Ingredient.RANGE) else "",
                "R: Area" if game_data.formula_builder.ingredient_unlocked(Ingredient.AREA) else "",
                "A: Cold" if game_data.formula_builder.ingredient_unlocked(Ingredient.COLD) else "",
                "S: Life" if game_data.formula_builder.ingredient_unlocked(Ingredient.LIFE) else "",
                "D: Shield" if game_data.formula_builder.ingredient_unlocked(Ingredient.SHIELD) else ""
            ])
            display_lines(surface, gfx_data.assets.font_message, ingredient_lines, 400, 65, ydiff=14)

        formulas = game_data.formula_builder.evaluate(caster=game_data.player)
        formula = formulas[game_data.formula_builder.currformula]

        surface = pygame.Surface(self.size.tuple())
        linediff = 14
        y = 5 * linediff
        display_text(surface, "Formulas", gfx_data.assets.font_message, (50, y))

        y += 3 * linediff
        text = "Formula {}/{}".format(game_data.formula_builder.currformula + 1, game_data.formula_builder.num_formula)
        display_text(surface, text, gfx_data.assets.font_message, (50, y))

        y += 2 * linediff
        display_text(surface, "Vial slots:", gfx_data.assets.font_message, (50, y))
        y += linediff
        for idx, form in enumerate(game_data.formula_builder.current_slots):
            text = "Slot {}: {}".format(idx+1, form.name)
            if idx == game_data.formula_builder.currslot:
                text += "<-- "
            display_text(surface, text, gfx_data.assets.font_message, (50, y))
            y += linediff

        y += linediff
        display_text(surface, "Formula stats:", gfx_data.assets.font_message, (50, y))

        if formula.suboptimal:
            y += linediff
            display_text(surface, "INFO: Combined heal/attack or attack modifier but no attack", gfx_data.assets.font_message, (50, y))

        y += linediff * 2
        cooldown_text = "Cooldown: {} rounds".format(formula.cooldown)
        display_text(surface, cooldown_text, gfx_data.assets.font_message, (50, y))

        y += linediff * 2
        lines = textwrap.wrap(formulas[game_data.formula_builder.currformula].text_stats, 60)
        display_lines(surface, gfx_data.assets.font_message, lines, 50, y, ydiff=13)
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

        draw_ingredient_list()

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
        do_quit = key_action.get(EventType.exit)
        if do_quit:
            if GameStates.STORY_SCREEN in game_data.prev_state: # between levels
                game_data.player.caster.set_formulas(game_data.formula_builder.evaluate())
                gfx_data.camera.initialize_map()
                gfx_data.camera.center_on(game_data.player.pos.x, game_data.player.pos.y)
                return self.close(game_data, StoryWindow)
            else: #after level up
                game_data.player.caster.set_formulas(game_data.formula_builder.evaluate())
                return self.close(game_data)

        slot = key_action.get("slot")
        if slot is not None:
            game_data.formula_builder.currslot = slot
            return {}

        ingredient = key_action.get("ingredient")
        if ingredient and game_data.formula_builder.ingredient_unlocked(ingredient):
            game_data.formula_builder.set_slot(game_data.formula_builder.currslot, ingredient)
            self.change_slot(game_data, 1)
            return {}

        next_formula = key_action.get("next_formula")
        if next_formula:
            self.change_formula(game_data, next_formula)
            return {}

        next_slot = key_action.get("next_slot")
        if next_slot:
            self.change_slot(game_data, next_slot)
            return {}

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(EventType.scroll_up)
        if scroll_up:
            self.change_slot(game_data, -1)

        scroll_down = mouse_action.get(EventType.scroll_down)
        if scroll_down:
            self.change_slot(game_data, 1)

        right_clicked = mouse_action.get(EventType.right_click)
        if right_clicked:
            self.change_formula(game_data, 1)

        left_clicked = mouse_action.get(EventType.left_click)
        if left_clicked:
            self.change_formula(game_data, -1)
