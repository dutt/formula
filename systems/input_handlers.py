import pygame
from attrdict import AttrDict

from components.ingredients import Ingredient
from components.events import EventType
from components.game_states import GameStates
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
import systems.input_recorder
import config


def get_current_modifier_keys():
    pressed_keys = pygame.key.get_pressed()
    modifier_keys = [pygame.K_LALT, pygame.K_RALT, pygame.K_RSHIFT, pygame.K_LSHIFT]
    modifiers = [key for key in modifier_keys if pressed_keys[key]]
    return modifiers


def handle_keys(events, state, modifiers=None):
    def handle_event(e):
        if state == GameStates.PLAY:
            return handle_player_turn_keys(e.key, modifiers)
        elif state == GameStates.LEVEL_UP:
            return handle_level_up_keys(e.key, modifiers)
        elif state == GameStates.TARGETING:
            return handle_targeting(e.key, modifiers)
        elif state == GameStates.FORMULA_SCREEN:
            return handle_formula_screen_keys(e.key, modifiers)
        elif state == GameStates.STORY_SCREEN:
            return handle_story_screen(e.key, modifiers)
        elif state == GameStates.ASK_QUIT:
            return handle_ask_quit(e.key, modifiers)
        elif state in [GameStates.VICTORY, GameStates.PLAYER_DEAD]:
            return handle_player_dead(e.key, modifiers)
        elif state == GameStates.CONSOLE:
            return handle_console(e.key, modifiers)
        elif state == GameStates.CRAFTING:
            return handle_crafting(e.key, modifiers)
        elif state == GameStates.INVENTORY:
            return handle_inventory(e.key, modifiers)
        elif state in [
            GameStates.CHARACTER_SCREEN,
            GameStates.WELCOME_SCREEN,
            GameStates.GENERAL_HELP_SCREEN,
            GameStates.FORMULA_HELP_SCEEN,
            GameStates.STORY_HELP_SCREEN,
            GameStates.CRAFTING_HELP,
            GameStates.INVENTORY_HELP,
        ]:
            return handle_general_keys(e.key, modifiers)
        else:
            raise ValueError("Input handler in unknown state")

    if not modifiers:
        modifiers = get_current_modifier_keys()

    for e in events:
        if not config.conf.is_replaying:
            systems.input_recorder.add_key_event(e)
        retr = handle_event(e)
        retr["event_id"] = e.event_id
        return retr
    return {}


def handle_targeting(key, modifiers):
    if key == pygame.K_w:
        return {EventType.move: (0, -1)}
    elif key == pygame.K_s:
        return {EventType.move: (0, 1)}
    elif key == pygame.K_a:
        return {EventType.move: (-1, 0)}
    elif key == pygame.K_d:
        return {EventType.move: (1, 0)}

    return handle_general_keys(key, modifiers)


def handle_inventory(key, modifiers):
    if key in [pygame.K_UP, pygame.K_w]:
        return {"up": 1}
    elif key in [pygame.K_DOWN, pygame.K_s]:
        return {"down": 1}
    elif key in [pygame.K_LEFT, pygame.K_a]:
        return {"left": 1}
    elif key in [pygame.K_RIGHT, pygame.K_d]:
        return {"right": 1}
    elif key >= pygame.K_1 and key <= pygame.K_9:  # quickslot assignments
        return {"assign": int(chr(key))}
    elif key == pygame.K_TAB:
        return {EventType.show_help: True}

    return handle_general_keys(key, modifiers)


def handle_crafting(key, modifiers):
    if key == pygame.K_q:
        return {"ingredient": Ingredient.EMPTY}
    elif key == pygame.K_w:
        return {"ingredient": Ingredient.FIRE}
    elif key == pygame.K_e:
        return {"ingredient": Ingredient.RANGE}
    elif key == pygame.K_r:
        return {"ingredient": Ingredient.AREA}
    elif key == pygame.K_a:
        return {"ingredient": Ingredient.WATER}
    elif key == pygame.K_s and config.conf.heal:
        return {"ingredient": Ingredient.LIFE}
    elif key == pygame.K_d:
        return {"ingredient": Ingredient.EARTH}
    elif key == pygame.K_DOWN:
        return {"next_slot": 1}
    elif key == pygame.K_UP:
        return {"next_slot": -1}
    elif key == pygame.K_SPACE:
        return {"apply": True}
    elif key == pygame.K_TAB:
        return {EventType.show_help: True}

    return handle_general_keys(key, modifiers)


def handle_console(key, modifiers):
    if pygame.K_RSHIFT in modifiers:
        if key == pygame.K_MINUS:
            return {"key": pygame.K_UNDERSCORE}
        elif key == pygame.K_0:
            return {"key": pygame.K_EQUALS}
        elif key == pygame.K_8:
            return {"key": pygame.K_LEFTPAREN}
        elif key == pygame.K_9:
            return {"key": pygame.K_RIGHTPAREN}
    if key >= pygame.K_a and key <= pygame.K_z:  # alphabet lowercase
        return {
            "key": key,
            "uppercase": pygame.K_RSHIFT in modifiers,
        }
    elif key >= pygame.K_0 and key <= pygame.K_9:  # numbers
        return {"key": key}
    elif key in [pygame.K_PERIOD, pygame.K_SPACE, pygame.K_COMMA]:
        return {"key": key}
    elif key == pygame.K_RETURN:
        return {"apply": True}
    elif key == pygame.K_BACKSPACE:
        return {"backspace": True}
    elif key == pygame.K_UP:
        return {"history": -1}
    elif key == pygame.K_DOWN:
        return {"history": 1}
    return handle_general_keys(key, modifiers)


def handle_ask_quit(key, modifiers):
    if key == pygame.K_SPACE:
        return {EventType.keep_playing: True}
    elif key == pygame.K_ESCAPE:
        return {EventType.exit: True}
    return handle_general_keys(key, modifiers)


def handle_player_dead(key, modifiers):
    if key == pygame.K_SPACE:
        return {EventType.keep_playing: True, EventType.exit: True}
    elif key == pygame.K_ESCAPE:
        return {EventType.exit: True}
    return handle_general_keys(key, modifiers)


def handle_story_screen(key, modifiers):
    if key == pygame.K_SPACE:
        return {"next": True}
    elif key == pygame.K_TAB:
        return {EventType.show_help: True}
    return handle_general_keys(key, modifiers)


def handle_formula_screen_keys(key, modifiers):
    if key == pygame.K_1:
        return {"formula": 0}
    elif key == pygame.K_2:
        return {"formula": 1}
    elif key == pygame.K_3:
        return {"formula": 2}
    elif key == pygame.K_4:
        return {"formula": 3}
    elif key == pygame.K_5:
        return {"formula": 4}
    elif key == pygame.K_q:
        return {"ingredient": Ingredient.EMPTY}
    elif key == pygame.K_w:
        return {"ingredient": Ingredient.WATER}
    elif key == pygame.K_e:
        return {"ingredient": Ingredient.FIRE}
    elif key == pygame.K_r:
        return {"ingredient": Ingredient.RANGE}
    elif key == pygame.K_a:
        return {"ingredient": Ingredient.AREA}
    elif key == pygame.K_s and config.conf.heal:
        return {"ingredient": Ingredient.LIFE}
    elif key == pygame.K_d:
        return {"ingredient": Ingredient.EARTH}
    elif key == pygame.K_LEFT:
        return {"next_formula": -1}
    elif key == pygame.K_RIGHT:
        return {"next_formula": 1}
    elif key == pygame.K_DOWN:
        return {"next_slot": 1}
    elif key == pygame.K_UP:
        return {"next_slot": -1}
    elif key == pygame.K_TAB:
        return {EventType.show_help: True}

    return handle_general_keys(key, modifiers)


def handle_general_keys(key, modifiers):
    if key in [pygame.K_ESCAPE, pygame.K_TAB, pygame.K_SPACE]:
        return {EventType.exit: True}
    elif key == pygame.K_RETURN and (pygame.K_RALT in modifiers or pygame.K_LALT in modifiers):
        return {EventType.fullscreen: True}
    elif key in [pygame.K_UP, pygame.K_w]:
        return {EventType.scroll_up: 1}
    elif key in [pygame.K_DOWN, pygame.K_s]:
        return {EventType.scroll_down: 1}
    elif key == 167:  # paragraph sign key, left of 1
        return {EventType.console: True}
    return {}


def handle_level_up_keys(key, modifiers):
    if key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
        return {EventType.level_up: True}
    elif key in [pygame.K_UP, pygame.K_w]:
        return {"choice": -1}
    elif key in [pygame.K_DOWN, pygame.K_s]:
        return {"choice": 1}
    return handle_general_keys(key, modifiers)


def handle_mouse(events, constants, camera, ignore_first_click, logger):
    def handle_event(e):
        pos = e.pos
        cx = (pos.x - constants.right_panel_size.width) // CELL_WIDTH
        cy = pos.y // CELL_HEIGHT
        cx, cy = camera.screen_to_map(cx, cy)
        data = {"type" : "mouse_event",
                "x": pos.x, "y": pos.y, "cx": cx, "cy": cy,
                "alternate": shift_pressed, "button" : e.button }
        logger.log(data, event_id=e.event_id)
        e.data = AttrDict(data)
        if not config.conf.is_replaying:
            systems.input_recorder.add_mouse_event(e)
        if e.button == 1:
            return {EventType.left_click: e.data}
        elif e.button == 3:
            return {EventType.right_click: e.data}
        elif e.button == 4:
            return {EventType.scroll_up: e.data}
        elif e.button == 5:
            return {EventType.scroll_down: e.data}

    if ignore_first_click:
        if events:
            logger.log({
                "type" : "ignored_mouse_events",
                "ids" : [e.event_id for e in events]
            }, attach_id=False)
        return {}
    modifiers = get_current_modifier_keys()
    shift_pressed = pygame.K_RSHIFT in modifiers or pygame.K_LSHIFT in modifiers
    for e in events:
            retr = handle_event(e)
            retr["event_id"] = e.event_id
            return retr
    return {}


def handle_player_turn_keys(key, modifiers):
    if key == pygame.K_w:
        return {EventType.move: (0, -1)}
    elif key == pygame.K_s:
        return {EventType.move: (0, 1)}
    elif key == pygame.K_a:
        return {EventType.move: (-1, 0)}
    elif key == pygame.K_d:
        return {EventType.move: (1, 0)}
    elif key in [pygame.K_SPACE, pygame.K_e]:
        return {EventType.interact: True}
    elif key == pygame.K_1:
        return {EventType.start_throwing_vial: 0}
    elif key == pygame.K_2:
        return {EventType.start_throwing_vial: 1}
    elif key == pygame.K_3:
        return {EventType.start_throwing_vial: 2}
    elif key == pygame.K_4:
        return {EventType.start_throwing_vial: 3}
    elif key == pygame.K_5:
        return {EventType.start_throwing_vial: 4}
    elif key == pygame.K_6:
        return {EventType.start_throwing_vial: 5}
    elif key == pygame.K_7:
        return {EventType.start_throwing_vial: 6}
    elif key == pygame.K_8:
        return {EventType.start_throwing_vial: 7}
    elif key == pygame.K_9:
        return {EventType.start_throwing_vial: 8}
    elif key == pygame.K_TAB:
        return {EventType.show_help: True}
    elif key == pygame.K_v:
        return {EventType.start_crafting: True}
    elif key == pygame.K_i:
        return {EventType.inventory: True}
    elif key == pygame.K_z:
        return {EventType.use_consumable: 0}
    elif key == pygame.K_x:
        return {EventType.use_consumable: 1}
    elif key == pygame.K_c:
        return {EventType.use_consumable: 2}

    return handle_general_keys(key, modifiers)
