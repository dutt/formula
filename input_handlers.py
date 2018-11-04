import tcod

from game_states import GameState


class Event:
    move = "move"
    fullscreen = "fullscreen"
    exit = "exit"
    pickup = "pickup"
    show_inventory = "show_inventory"
    inventory_index = "inventory_index"
    drop_inventory = "drop_inventory"
    left_click = "left_click"
    right_click = "right_click"
    take_stairs = "take_stairs"
    level_up = "level_up"
    character_screen = "character_screen"
    wait = "wait"
    spellmaker_screen = "spellmaker"
    start_casting_spell = "start_casting_spell"
    show_help = "show_help"

def handle_keys(key, state):
    if state == GameState.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif state == GameState.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif state in [GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY]:
        return handle_inventory_keys(key)
    elif state == GameState.TARGETING:
        return handle_targeting_keys(key)
    elif state == GameState.LEVEL_UP:
        return handle_level_up_keys(key)
    elif state == GameState.CHARACTER_SCREEN:
        return handle_character_screen_keys(key)
    elif state == GameState.SPELLMAKER_SCREEN:
        return handle_spellmaker_screen_keys(key)
    elif state == GameState.SHOW_HELP:
        return handle_help_keys(key)
    return {}


from components.ingredients import Ingredient


def handle_spellmaker_screen_keys(key):
    key_char = chr(key.c)
    if key.vk == tcod.KEY_ESCAPE or key_char == 'm':
        return {Event.exit: True}
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
    if key_char == 'q':
        return {"ingredient": Ingredient.FIRE}
    elif key_char == 'w':
        return {"ingredient": Ingredient.RANGE}
    elif key_char == 'e':
        return {"ingredient": Ingredient.AREA}
    elif key.vk == tcod.KEY_TAB:
        return {"next_spell": True}
    return {}


def handle_help_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {Event.exit: True}
    elif key.vk == tcod.KEY_TAB:
        return {Event.exit: True}
    return {}


def handle_character_screen_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {Event.exit: True}
    return {}


def handle_level_up_keys(key):
    if key:
        key_char = chr(key.c)
        if key_char == 'a':
            return {Event.level_up: "hp"}
        elif key_char == 'b':
            return {Event.level_up: "str"}
        elif key_char == 'c':
            return {Event.level_up: "def"}
    return {}


def handle_targeting_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {Event.exit: True}
    return {}


def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)
    if mouse.lbutton_pressed:
        return {Event.left_click: (x, y)}
    elif mouse.rbutton_pressed:
        return {Event.right_click: (x, y)}
    return {}


def handle_inventory_keys(key):
    index = key.c - ord('a')
    if index >= 0:
        return {Event.inventory_index: index}
    elif key.vk == tcod.KEY_ENTER and key.lalt:
        return {Event.fullscreen: True}
    elif key.vk == tcod.KEY_ESCAPE:
        return {Event.exit: True}
    return {}


def handle_player_dead_keys(key):
    key_char = chr(key.c)
    if key_char == 'i':
        return {Event.show_inventory: True}
    elif key.vk == tcod.KEY_ENTER and key.lalt:
        return {Event.fullscreen: True}
    elif key.vk == tcod.KEY_ESCAPE:
        return {Event.exit: True}
    return {}


def handle_player_turn_keys(key):
    key_char = chr(key.c)

    if key.vk == tcod.KEY_UP or key_char == 'k':
        return {Event.move: (0, - 1)}
    elif key.vk == tcod.KEY_DOWN or key_char == 'j':
        return {Event.move: (0, 1)}
    elif key.vk == tcod.KEY_LEFT or key_char == 'h':
        return {Event.move: (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT or key_char == 'l':
        return {Event.move: (1, 0)}
    elif key_char == 'y':
        return {Event.move: (-1, -1)}
    elif key_char == 'u':
        return {Event.move: (1, -1)}
    elif key_char == 'b':
        return {Event.move: (-1, 1)}
    elif key_char == 'n':
        return {Event.move: (1, 1)}
    elif key_char == 'z':
        return {Event.wait: True}
    elif key.vk == tcod.KEY_1:
        return {Event.start_casting_spell: 0}
    elif key.vk == tcod.KEY_2:
        return {Event.start_casting_spell: 1}
    elif key.vk == tcod.KEY_3:
        return {Event.start_casting_spell: 2}
    elif key.vk == tcod.KEY_4:
        return {Event.start_casting_spell: 3}
    elif key.vk == tcod.KEY_5:
        return {Event.start_casting_spell: 4}
    elif key_char == 'g':
        return {Event.pickup: True}
    elif key_char == 'i':
        return {Event.show_inventory: True}
    elif key_char == 'd':
        return {Event.drop_inventory: True}
    elif key_char == 'c':
        return {Event.character_screen: True}
    elif key_char == 'm':
        return {Event.spellmaker_screen: True}
    elif key.vk == tcod.KEY_TAB:
        return {Event.show_help: True}
    elif key.vk == tcod.KEY_ENTER:
        return {Event.take_stairs: True}

    elif key.vk == tcod.KEY_ENTER and key.lalt:
        return {Event.fullscreen: True}
    elif key.vk == tcod.KEY_ESCAPE:
        return {Event.exit: True}

    return {}
