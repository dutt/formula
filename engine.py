import os, sys

import tcod

from death import kill_player, kill_monster
from loader_functions.init_new_game import get_constants, get_game_variables

def play_game(game_data):
    while not tcod.console_is_window_closed():

        """if state == GameState.ENEMY_TURN:
            for e in entities:
                if e.ai:
                    enemy_results = e.ai.take_turn(player, fov_map, gmap, entities)
                    for res in enemy_results:
                        msg = res.get("message")
                        if msg:
                            game_data.log.add_message(msg)

                if state == GameState.PLAYER_DEAD:
                    break
            else:
                state = GameState.PLAY
        """

        for res in game_data.timesystem.tick(game_data=game_data):
            msg = res.get("message")
            if msg:
                game_data.log.add_message(msg)

            dead_entity = res.get("dead")
            if dead_entity:
                if dead_entity == game_data.player:
                    msg, game_data = kill_player(dead_entity, game_data)
                else:
                    msg, game_data = kill_monster(dead_entity, game_data)
                game_data.log.add_message(msg)

            cast = res.get("cast")
            if cast is not None:
                if cast:
                    spell = res.get("spell")
                    game_data.player.caster.add_cooldown(spell.spellidx,
                                                         spell.cooldown+1)
            quit = res.get("quit")
            if quit:
                return

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    constants = get_constants()
    game_data, state = get_game_variables(constants)
    tcod.console_set_custom_font(resource_path('data/arial12x12.png'),
                                 tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    tcod.console_init_root(constants.screen_size.width, constants.screen_size.height, "spellmaker", False)

    con = tcod.console_new(constants.screen_size.width, constants.screen_size.height)
    bottom_panel = tcod.console_new(constants.screen_size.width, constants.bottom_panel_height)
    right_panel = tcod.console_new(constants.right_panel_size.width, constants.right_panel_size.height)

    game_data.player.set_gui(con, bottom_panel, right_panel)
    game_data.player.set_initial_state(state, game_data)
    play_game(game_data)

    with open("messages.log", 'w') as writer:
        for msg in game_data.log.messages:
            writer.write(msg)


if __name__ == '__main__':
    try:
        main()
    except:
        import traceback

        tb = traceback.format_exc()
        print(tb)
        try:
            with open("crash.log", 'w') as writer:
                writer.write(tb)
        except:
            print("failed to write crashlog:")
            traceback.print_exc()
