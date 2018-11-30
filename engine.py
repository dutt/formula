import contextlib
import traceback

with contextlib.redirect_stdout(None):
    import pygame

from death import kill_player, kill_monster
from loader_functions.init_new_game import get_constants, setup_data_state
from messages import Message
from game_states import GameStates


def play_game(game_data, gfx_data):
    while True:
        for res in game_data.timesystem.tick(game_data, gfx_data):
            try:
                msg = res.get("message")
                if msg:
                    game_data.log.add_message(msg)

                dead_entity = res.get("dead")
                if dead_entity:
                    if dead_entity == game_data.player:
                        msg, game_data = kill_player(game_data, gfx_data.assets)
                    else:
                        msg, game_data = kill_monster(dead_entity, game_data, gfx_data.assets)
                    game_data.log.add_message(msg)

                cast = res.get("cast")
                if cast is not None:
                    if cast:
                        formula = res.get("formula")
                        game_data.player.caster.add_cooldown(formula.formula_idx,
                                                             formula.cooldown + 1)
                do_quit = res.get("quit")
                if do_quit:
                    return

                xp = res.get("xp")
                if xp:
                    leveled_up = game_data.player.level.add_xp(xp)
                    game_data.log.add_message(Message("You gain {} xp".format(xp)))
                    if leveled_up:
                        game_data.log.add_message(
                                Message(
                                    "You grow stronger, reached level {}".format(game_data.player.level.current_level),
                                    (0, 255, 0)))
                        game_data.prev_state.append(game_data.state)
                        game_data.state = GameStates.LEVEL_UP
            except AttributeError:
                print("Failed to handle res={}".format(res))
                traceback.print_exc()


def setup_prevstate(state):
    retr = []

    if state == GameStates.PLAY:
        return retr
    retr.append(GameStates.PLAY)

    if state == GameStates.FORMULA_SCREEN:
        return retr
    retr.append(GameStates.FORMULA_SCREEN)

    if state == GameStates.STORY_SCREEN:
        return retr
    retr.append(GameStates.STORY_SCREEN)

    return retr

def main():
    constants = get_constants()
    game_data, gfx_data, state = setup_data_state(constants)

    game_data.state = state
    game_data.prev_state = setup_prevstate(state)

    gfx_data.camera.center_on(game_data.player.pos.x, game_data.player.pos.y)

    play_game(game_data, gfx_data)

    pygame.quit()

    with open("messages.log", 'w') as writer:
        for msg in game_data.log.messages:
            writer.write(msg.text)


if __name__ == '__main__':
    try:
        main()
    except:
        tb = traceback.format_exc()
        print(tb)
        try:
            with open("crash.log", 'w') as writer:
                writer.write(tb)
        except:
            print("failed to write crashlog:")
            traceback.print_exc()
