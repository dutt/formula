import textwrap

import pygame
from attrdict import AttrDict

from components.game_states import GameStates
from components.ingredients import Ingredient
from graphics.display_helpers import display_text, display_lines
from graphics.story_window import StoryWindow
from graphics.window import Window, ClickableLabel
from graphics.textwindow import TextWindow
from systems.input_handlers import EventType
from util import resource_path, Pos, Size
import config

class FormulaHelpWindow(TextWindow):
    PATH = resource_path("data/help/formula_window.txt")

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, path=FormulaHelpWindow.PATH, next_window=None)


class IngredientMarker(ClickableLabel):
    def __init__(self, pos, text, ingredient, parent):
        super().__init__(pos=pos, text=text, size=Size(100, 30))
        self.ingredient = ingredient
        self.parent = parent

    def handle_click(self, game_data, gfx_data, mouse_action):
        left_click = mouse_action.get(EventType.left_click)
        if left_click:
            print(f"{self.ingredient} clicked")
            game_data.formula_builder.set_slot(game_data.formula_builder.currslot, self.ingredient)
            self.parent.change_slot(game_data, 1)
        return {}

    def is_clicked(self, mouse_action):
        if "left_click" not in mouse_action:
            return False
        left_click = AttrDict(mouse_action["left_click"])
        left_click.x -= self.parent.pos.x
        left_click.y -= self.parent.pos.y
        return super().is_clicked({"left_click" : left_click})

    def draw(self, surface, game_data, gfx_data):
        display_text(surface, self.text, gfx_data.assets.font_message, self.pos.tuple())

        x1 = self.pos.x
        x2 = self.pos.x + self.size.width
        y1 = self.pos.y
        y2 = self.pos.y + self.size.height
        color = (255, 0, 0)
        #pygame.draw.line(surface, color, (x1, y1), (x1, y2), 2)
        #pygame.draw.line(surface, color, (x1, y1), (x2, y1), 2)
        #pygame.draw.line(surface, color, (x2, y1), (x2, y2), 2)
        #pygame.draw.line(surface, color, (x1, y2), (x2, y2), 2)

class FormulaWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.ingredient_markers = []

    def draw_ingredient_list(self, surface, game_data, gfx_data):
        ingredient_lines = []
        ingredient_to_key_map = [
            [ [Ingredient.EMPTY], "Q" ],
            [ [Ingredient.FIRE, Ingredient.INFERNO, Ingredient.FIREBOLT, Ingredient.FIRESPRAY], "W"],
            [ [Ingredient.WATER, Ingredient.SLEET, Ingredient.ICE, Ingredient.ICE_VORTEX, Ingredient.ICEBOLT], "E"],
            [ [Ingredient.RANGE], "R"],
            [ [Ingredient.AREA], "A"],
            [ [Ingredient.LIFE, Ingredient.VITALITY], "S"],
            [ [Ingredient.EARTH, Ingredient.MUD, Ingredient.MAGMA, Ingredient.ROCK], "D"]
        ]
        choices = game_data.formula_builder.current_ingredient_choices()
        for ing in choices:
            for group, key in ingredient_to_key_map:
                if ing in group:
                    ingredient_lines.append(f"{key}: {ing.name}")

        def get_ingredient_list_key(item):
            mapping = {
                "Q": 0,
                "W": 1,
                "E": 2,
                "R": 3,
                "A": 4,
                "S": 5,
                "D": 6,
            }
            return mapping[item[0]]

        ingredient_lines = sorted(ingredient_lines, key=get_ingredient_list_key)
        display_lines(surface, gfx_data.assets.font_message, ingredient_lines, 400, 120)

    def draw_counted_ingredient_list(self, surface, game_data, gfx_data):
        ingredient_lines = []
        ingredient_to_key_map = [
            [ [Ingredient.EMPTY], "Q" ],
            [ [Ingredient.FIRE, Ingredient.INFERNO, Ingredient.FIREBOLT, Ingredient.FIRESPRAY], "W"],
            [ [Ingredient.WATER, Ingredient.SLEET, Ingredient.ICE, Ingredient.ICE_VORTEX, Ingredient.ICEBOLT], "E"],
            [ [Ingredient.RANGE], "R"],
            [ [Ingredient.AREA], "A"],
            [ [Ingredient.LIFE, Ingredient.VITALITY], "S"],
            [ [Ingredient.EARTH, Ingredient.MUD, Ingredient.MAGMA, Ingredient.ROCK], "D"]
        ]
        choices = game_data.formula_builder.current_ingredient_choices()
        for ing in choices:
            for group, key in ingredient_to_key_map:
                if ing in group:
                    if ing == Ingredient.EMPTY:
                        ingredient_lines.append(f"{key}: {ing.name}")
                    else:
                        count = game_data.ingredient_storage.count_left(ing, game_data.formula_builder)
                        ingredient_lines.append(f"{key}: {ing.name}, {count} left")

        def get_ingredient_list_key(item):
            mapping = {
                "Q": 0,
                "W": 1,
                "E": 2,
                "R": 3,
                "A": 4,
                "S": 5,
                "D": 6,
            }
            return mapping[item[0]]

        ingredient_lines = sorted(ingredient_lines, key=get_ingredient_list_key)
        display_lines(surface, gfx_data.assets.font_message, ingredient_lines, 400, 120)

    def draw_crafted_ingredient_list(self, surface, game_data, gfx_data):
        counts = game_data.ingredient_storage.remaining(game_data.formula_builder)

        x = 450
        y = 120

        self.ingredient_markers = []
        self.ingredient_markers.append(IngredientMarker(Pos(x, y), "Empty", Ingredient.EMPTY, parent=self))
        y += 40
        for ing, count in counts.items():
            if count <= 0:
                continue
            text = "{}, {} left".format(ing.name.capitalize(), count)
            self.ingredient_markers.append(IngredientMarker(Pos(x, y), text, ing, parent=self))
            y += 40

        for im in self.ingredient_markers:
            im.draw(surface, game_data, gfx_data)

    def draw(self, game_data, gfx_data):
        formulas = game_data.formula_builder.evaluate_entity(caster=game_data.player)
        formula = formulas[game_data.formula_builder.currformula]

        surface = pygame.Surface(self.size.tuple())
        linediff = gfx_data.assets.font_message_height

        if game_data.map.tutorial:
            lines = [
                "TUTORIAL: This is just to show you your current formulas for the tutorial",
            ]
            if not config.conf.pickup:
                lines.append("After this tutorial you'll be able to select these as you want")
            else:
                lines.append("After this tutorial you'll be able to find ingredients on the levels")

            display_lines(surface, gfx_data.assets.font_message, lines, 00, 20)

        y = 120
        display_text(surface, "Formulas", gfx_data.assets.font_message, (50, y))

        y += 3 * linediff
        text = "Formula {}/{}".format(game_data.formula_builder.currformula + 1, game_data.formula_builder.num_formula,)
        display_text(surface, text, gfx_data.assets.font_message, (50, y))

        y += 2 * linediff
        display_text(surface, "Vial slots:", gfx_data.assets.font_message, (50, y))
        y += linediff
        for idx, form in enumerate(game_data.formula_builder.current_slots):
            text = "Slot {}: {}".format(idx + 1, form.name)
            if idx == game_data.formula_builder.currslot:
                text += "<-- "
            display_text(surface, text, gfx_data.assets.font_message, (50, y))
            y += linediff

        y += linediff
        display_text(surface, "Formula stats:", gfx_data.assets.font_message, (50, y))

        if formula.suboptimal:
            y += linediff
            display_text(
                surface,
                "INFO: Combined heal/attack or attack modifier but no attack",
                gfx_data.assets.font_message,
                (50, y),
            )

        y += linediff * 2
        cooldown_text = "Cooldown: {} rounds".format(formula.cooldown)
        display_text(surface, cooldown_text, gfx_data.assets.font_message, (50, y))

        y += linediff * 2
        lines = textwrap.wrap(formulas[game_data.formula_builder.currformula].text_stats, 60)
        display_lines(surface, gfx_data.assets.font_message, lines, 50, y)
        y += len(lines) * linediff

        y += 2 * linediff
        display_text(
            surface, "Arrow left/right or 1,2,3,...: select formula", gfx_data.assets.font_message, (50, y),
        )
        y += linediff
        display_text(
            surface, "Arrow up/down or Mouse scroll: select slot", gfx_data.assets.font_message, (50, y),
        )
        y += linediff
        display_text(
            surface, "Press Tab for help, or Space to confirm selection", gfx_data.assets.font_message, (50, y),
        )

        if config.conf.pickup:
            if config.conf.crafting:
                self.draw_crafted_ingredient_list(surface, game_data, gfx_data)
            else:
                self.draw_counted_ingredient_list(surface, game_data, gfx_data)
        else:
            self.draw_ingredient_list(surface, game_data, gfx_data)

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
            game_data.player.caster.set_formulas(game_data.formula_builder.evaluate_entity(game_data.player))
            game_data.formula_builder.currformula = 0
            return self.close(game_data, activate_for_new_state=True)

        formula = key_action.get("formula")
        if formula is not None and formula < game_data.formula_builder.num_formula:
            game_data.formula_builder.currformula = formula

        ingredient = key_action.get("ingredient")
        if ingredient and game_data.formula_builder.ingredient_unlocked(ingredient) and not game_data.map.tutorial:
            if config.conf.pickup and ingredient != Ingredient.EMPTY:
                count = game_data.ingredient_storage.count_left(ingredient, game_data.formula_builder)
                if count < 1:
                    return
            game_data.formula_builder.set_slot(game_data.formula_builder.currslot, ingredient)
            self.change_slot(game_data, 1)

        next_formula = key_action.get("next_formula")
        if next_formula:
            self.change_formula(game_data, next_formula)

        next_slot = key_action.get("next_slot")
        if next_slot:
            self.change_slot(game_data, next_slot)

    def handle_click(self, game_data, gfx_data, mouse_action):
        if config.conf.crafting and not game_data.map.tutorial:
            for im in self.ingredient_markers:
                if im.is_clicked(mouse_action):
                    return im.handle_click(game_data, gfx_data, mouse_action)

        scroll_up = mouse_action.get(EventType.scroll_up)
        if scroll_up:
            self.change_slot(game_data, -1)

        scroll_down = mouse_action.get(EventType.scroll_down)
        if scroll_down:
            self.change_slot(game_data, 1)
