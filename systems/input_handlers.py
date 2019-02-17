import pygame
from attrdict import AttrDict

from components.ingredients import Ingredient
from components.events import EventType
from components.game_states import GameStates
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
import systems.input_recorder


def handle_keys(events, state):
    pressed_keys = pygame.key.get_pressed()
    modifiers = [key for key in [pygame.K_LALT, pygame.K_RALT] if pressed_keys[key]]

    for e in events:
        systems.input_recorder.add_key_event(e)
        if state == GameStates.PLAY:
            return handle_player_turn_keys(e.key, modifiers)
        elif state == GameStates.LEVEL_UP:
            return handle_level_up_keys(e.key, modifiers)
        elif state in [GameStates.CHARACTER_SCREEN,
                       GameStates.WELCOME_SCREEN,
                       GameStates.TARGETING,
                       GameStates.GENERAL_HELP_SCREEN,
                       GameStates.FORMULA_HELP_SCEEN,
                       GameStates.STORY_HELP_SCREEN]:
            return handle_general_keys(e.key, modifiers)
        elif state == GameStates.FORMULA_SCREEN:
            return handle_formula_screen_keys(e.key, modifiers)
        elif state == GameStates.STORY_SCREEN:
            return handle_story_screen(e.key, modifiers)
        elif state == GameStates.ASK_QUIT:
            return handle_ask_quit(e.key, modifiers)
        elif state in [GameStates.VICTORY, GameStates.PLAYER_DEAD]:
            return handle_player_dead(e.key, modifiers)
    return {}


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
        return {"slot": 0}
    elif key == pygame.K_2:
        return {"slot": 1}
    elif key == pygame.K_3:
        return {"slot": 2}
    elif key == pygame.K_4:
        return {"slot": 3}
    elif key == pygame.K_5:
        return {"slot": 4}
    elif key == pygame.K_q:
        return {"ingredient": Ingredient.EMPTY}
    elif key == pygame.K_w:
        return {"ingredient": Ingredient.FIRE}
    elif key == pygame.K_e:
        return {"ingredient": Ingredient.RANGE}
    elif key == pygame.K_r:
        return {"ingredient": Ingredient.AREA}
    elif key == pygame.K_a:
        return {'ingredient': Ingredient.COLD}
    elif key == pygame.K_s:
        return {'ingredient': Ingredient.LIFE}
    elif key == pygame.K_d:
        return {'ingredient': Ingredient.SHIELD}
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

    return {}


def handle_level_up_keys(key, modifiers):
    if key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
        return {EventType.level_up: True}
    elif key in [pygame.K_UP, pygame.K_w]:
        return {"choice": -1}
    elif key in [pygame.K_DOWN, pygame.K_s]:
        return {"choice": 1}
    return handle_general_keys(key, modifiers)


def handle_mouse(events, constants, camera):
    pos = pygame.mouse.get_pos()
    for e in events:
        systems.input_recorder.add_mouse_event(e)
        cx = (pos[0] - constants.right_panel_size.width) // CELL_WIDTH
        cy = pos[1] // CELL_HEIGHT
        cx, cy = camera.screen_to_map(cx, cy)
        data = AttrDict({
            "x": pos[0],
            "y": pos[1],
            "cx": cx,
            "cy": cy,
        })
        if e.button == 1:
            return {EventType.left_click: data}
        elif e.button == 3:
            return {EventType.right_click: data}
        elif e.button == 4:
            return {EventType.scroll_up: data}
        elif e.button == 5:
            return {EventType.scroll_down: data}
    return {}


def handle_player_turn_keys(key, modifiers):
    if key == pygame.K_w:
        return {EventType.move: (0, - 1)}
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

    return handle_general_keys(key, modifiers)