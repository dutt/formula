import time

import pygame

from components.ingredients import Ingredient
from game_states import GameStates


class Event:
    move = "move"
    fullscreen = "fullscreen"
    exit = "exit"
    left_click = "left_click"
    right_click = "right_click"
    level_up = "level_up"
    character_screen = "character_screen"
    spellmaker_screen = "spellmaker"
    start_casting_spell = "start_casting_spell"
    show_help = "show_help"
    interact = "interact"


def handle_keys(state):
    while True:
        e = pygame.event.wait()
        if e.type == pygame.KEYDOWN:
            if state == GameStates.PLAY:
                return handle_player_turn_keys(e.key)
            elif state == GameStates.PLAYER_DEAD:
                return handle_player_dead_keys(e.key)
            elif state == GameStates.LEVEL_UP:
                return handle_level_up_keys(e.key)
            elif state in [GameStates.CHARACTER_SCREEN,
                           GameStates.WELCOME_SCREEN,
                           GameStates.TARGETING,
                           GameStates.GENERAL_HELP_SCREEN,
                           GameStates.SPELLMAKER_HELP_SCEEN]:
                return handle_general_keys(e.key)
            elif state == GameStates.SPELLMAKER_SCREEN:
                return handle_spellmaker_screen_keys(e.key)
            return {}
        time.sleep(0.01)


def handle_spellmaker_screen_keys(key):
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
    #    elif key == pygame.K_a:
    #        return {'ingredient' : Ingredient.COLD}
    elif key == pygame.K_s:
        return {'ingredient': Ingredient.LIFE}
    # elif key == pygame.K_d:
    #    return {'ingredient' : Ingredient.SHIELD}
    elif key == pygame.K_LEFT:
        return {"next_spell": -1}
    elif key == pygame.K_RIGHT:
        return {"next_spell": 1}
    elif key == pygame.K_DOWN:
        return {"next_slot": 1}
    elif key == pygame.K_UP:
        return {"next_slot": -1}
    elif key == pygame.K_TAB:
        return {Event.show_help: True}

    return handle_general_keys(key)


def handle_general_keys(key):
    if key == pygame.K_ESCAPE:
        return {Event.exit: True}
    elif key == pygame.K_TAB:
        return {Event.exit: True}
    elif key == pygame.K_RETURN and key.lalt:
        return {Event.fullscreen: True}
    return {}


def handle_level_up_keys(key):
    if key == pygame.K_a:
        return {Event.level_up: "hp"}
    elif key == pygame.K_b:
        return {Event.level_up: "str"}
    elif key == pygame.K_c:
        return {Event.level_up: "def"}
    return handle_general_keys(key)


def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)
    if mouse.lbutton_pressed:
        return {Event.left_click: (x, y)}
    elif mouse.rbutton_pressed:
        return {Event.right_click: (x, y)}
    return {}


def handle_player_dead_keys(key):
    return handle_general_keys(key)


def handle_player_turn_keys(key):
    if key == pygame.K_w:
        return {Event.move: (0, - 1)}
    elif key == pygame.K_s:
        return {Event.move: (0, 1)}
    elif key == pygame.K_a:
        return {Event.move: (-1, 0)}
    elif key == pygame.K_d:
        return {Event.move: (1, 0)}
    elif key == pygame.K_e:
        return {Event.interact: True}
    elif key == pygame.K_1:
        return {Event.start_casting_spell: 0}
    elif key == pygame.K_2:
        return {Event.start_casting_spell: 1}
    elif key == pygame.K_3:
        return {Event.start_casting_spell: 2}
    # elif key == pygame.K_4:
    #    return {Event.start_casting_spell: 3}
    # elif key == pygame.K_5:
    #    return {Event.start_casting_spell: 4}
    # elif key == pygame.K_c:
    #    return {Event.character_screen: True}
    elif key == pygame.K_TAB:
        return {Event.show_help: True}

    return handle_general_keys(key)
