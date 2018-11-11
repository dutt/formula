import tcod

from game_states import GameStates
from components.ingredients import Ingredient


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

def handle_keys(key, state):
    if state == GameStates.PLAY:
        return handle_player_turn_keys(key)
    elif state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif state == GameStates.LEVEL_UP:
        return handle_level_up_keys(key)
    elif state in [GameStates.CHARACTER_SCREEN,
                   GameStates.WELCOME_SCREEN,
                   GameStates.TARGETING,
                   GameStates.GENERAL_HELP_SCREEN,
                   GameStates.SPELLMAKER_HELP_SCEEN]:
        return handle_general_keys(key)
    elif state == GameStates.SPELLMAKER_SCREEN:
        return handle_spellmaker_screen_keys(key)
    return {}


def handle_spellmaker_screen_keys(key):
    key_char = chr(key.c)
    if key.pressed:
        key = key
    if key.vk == tcod.KEY_1:
        return {"slot": 0}
    elif key.vk == tcod.KEY_2:
        return {"slot": 1}
    elif key.vk == tcod.KEY_3:
        return {"slot": 2}
    elif key.vk == tcod.KEY_4:
        return {"slot": 3}
    elif key.vk == tcod.KEY_5:
        return {"slot": 4}
    elif key_char == 'q':
        return {"ingredient": Ingredient.EMPTY}
    elif key_char == 'w':
        return {"ingredient": Ingredient.FIRE}
    elif key_char == 'e':
        return {"ingredient": Ingredient.RANGE}
    elif key_char == 'r':
        return {"ingredient": Ingredient.AREA}
#    elif key_char == 'a':
#        return {'ingredient' : Ingredient.COLD}
    elif key_char == 's':
        return {'ingredient' : Ingredient.LIFE}
    #elif key_char == 'd':
    #    return {'ingredient' : Ingredient.SHIELD}
    elif key.vk == tcod.KEY_LEFT:
        return {"next_spell": -1}
    elif key.vk == tcod.KEY_RIGHT:
        return {"next_spell": 1}
    elif key.vk == tcod.KEY_DOWN:
        return {"next_slot": 1}
    elif key.vk == tcod.KEY_UP:
        return {"next_slot": -1}
    elif key.vk == tcod.KEY_TAB:
        return {Event.show_help: True}

    return handle_general_keys(key)


def handle_general_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {Event.exit: True}
    elif key.vk == tcod.KEY_TAB:
        return {Event.exit: True}
    elif key.vk == tcod.KEY_ENTER and key.lalt:
        return {Event.fullscreen: True}
    return {}


def handle_level_up_keys(key):
    key_char = chr(key.c)
    if key_char == 'a':
        return {Event.level_up: "hp"}
    elif key_char == 'b':
        return {Event.level_up: "str"}
    elif key_char == 'c':
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
    key_char = chr(key.c)

    if key_char == 'w':
        return {Event.move: (0, - 1)}
    elif key_char == 's':
        return {Event.move: (0, 1)}
    elif key_char == 'a':
        return {Event.move: (-1, 0)}
    elif key_char == 'd':
        return {Event.move: (1, 0)}
    elif key_char == 'e':
        return {Event.interact: True}
    elif key.vk == tcod.KEY_1:
        return {Event.start_casting_spell: 0}
    elif key.vk == tcod.KEY_2:
        return {Event.start_casting_spell: 1}
    elif key.vk == tcod.KEY_3:
        return {Event.start_casting_spell: 2}
    #elif key.vk == tcod.KEY_4:
    #    return {Event.start_casting_spell: 3}
    #elif key.vk == tcod.KEY_5:
    #    return {Event.start_casting_spell: 4}
    #elif key_char == 'c':
    #    return {Event.character_screen: True}
    elif key.vk == tcod.KEY_TAB:
        return {Event.show_help: True}

    return handle_general_keys(key)
