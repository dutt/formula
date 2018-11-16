import contextlib
with contextlib.redirect_stdout(None):
    import pygame

from components.pygame_gfx import initialize
from death import kill_player, kill_monster
from loader_functions.init_new_game import get_constants, get_game_variables


def play_game(game_data, assets):
    while True:
        for res in game_data.timesystem.tick(game_data=game_data):
            msg = res.get("message")
            if msg:
                game_data.log.add_message(msg)

            dead_entity = res.get("dead")
            if dead_entity:
                if dead_entity == game_data.player:
                    msg, game_data = kill_player(game_data, assets)
                else:
                    msg, game_data = kill_monster(dead_entity, game_data, assets)
                game_data.log.add_message(msg)

            cast = res.get("cast")
            if cast is not None:
                if cast:
                    spell = res.get("spell")
                    game_data.player.caster.add_cooldown(spell.spellidx,
                                                         spell.cooldown + 1)
            quit = res.get("quit")
            if quit:
                return


def main():
    constants = get_constants()
    gfx_data = initialize(constants)
    game_data, state = get_game_variables(constants, gfx_data)

    game_data.player.set_gui(gfx_data)
    game_data.player.set_initial_state(state, game_data)
    play_game(game_data, gfx_data.assets)

    pygame.quit()

    with open("messages.log", 'w') as writer:
        for msg in game_data.log.messages:
            writer.write(msg.text)


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
