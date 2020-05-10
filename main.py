import contextlib
import datetime
import json
import os
import traceback

with contextlib.redirect_stdout(None):
    import pygame

from attrdict import AttrDict

from loader_functions.init_new_game import get_constants, setup_data_state
from systems.death import kill_player, kill_monster
from systems.messages import Message
from systems import input_recorder, tester, balance_statistics, serialization
from components.game_states import GameStates
import config


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
                        gfx_data.windows.activate_wnd_for_state(game_data.state, game_data, gfx_data)
                    else:
                        game_data.stats.monster_killed(dead_entity)
                        msg, game_data = kill_monster(dead_entity, game_data, gfx_data.assets)
                    game_data.log.add_message(msg)

                cast = res.get("cast")
                if cast is not None:
                    if cast:
                        formula = res.get("formula")
                        game_data.stats.throw_vial(formula)
                        if config.conf.cooldown_mode == "always":
                            game_data.player.caster.add_cooldown(formula.formula_idx, formula.cooldown + 1)
                        else:
                            game_data.player.caster.add_cooldown(formula.formula_idx, formula.cooldown)
                do_quit = res.get("quit")
                if do_quit:
                    keep_playing = res.get("keep_playing")
                    return keep_playing == True  # handle False and None

                xp = res.get("xp")
                if xp:
                    leveled_up = game_data.player.level.add_xp(xp)
                    # leveled_up = game_data.player.level.add_xp(game_data.player.level.xp_to_next_level)
                    if not config.conf.keys:
                        game_data.log.add_message(Message("You gain {} xp".format(xp)))
                    if leveled_up:
                        game_data.log.add_message(
                            Message(
                                "You grow stronger, reached level {}".format(game_data.player.level.current_level),
                                (0, 255, 0),
                            )
                        )
                        game_data.prev_state.append(game_data.state)
                        game_data.state = GameStates.LEVEL_UP
                        game_data.menu_data.currchoice = 0
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

    if state == GameStates.WELCOME_SCREEN:
        return retr
    retr.append(GameStates.WELCOME_SCREEN)

    return retr


def set_seed():
    import random
    import config

    if config.conf.random_seed == "now":
        import datetime

        now = datetime.datetime.now()
        seed = str(now)
    else:
        seed = config.conf.random_seed

    # debugging seeds
    # seed = "2018-12-30 09:38:04.303108"
    # seed = "2019-01-25 22:19:22.597013"

    # seed = "2020-03-15 08:47:05.439709"
    # seed = "2020-04-04 21:01:02.999223"
    # seed = "2020-04-09 22:27:51.380348"
    # seed = "2020-04-23 20:50:35.897020"
    seed = "2020-05-09 09:44:45.558700"
    print("Using seed: <{}>".format(seed))
    random.seed(seed)
    return seed


def do_setup(constants, previous_data=None):
    game_data, gfx_data, state = setup_data_state(constants, run_tutorial=previous_data is None, previous_data=previous_data)

    game_data.prev_state = setup_prevstate(state)

    game_data.run_planner.generate(game_data)

    gfx_data.camera.initialize_map()
    gfx_data.camera.center_on(game_data.player.pos.x, game_data.player.pos.y)

    return game_data, gfx_data


def write_logs(game_data, seed, start_time, crashed):
    def serialize_end_state():
        data = {
            "hp": game_data.player.fighter.hp,
            "cooldowns": game_data.player.caster.cooldowns,
            "pos" : game_data.player.pos.tuple()
        }
        if game_data.player.fighter.shield:
            data["shield"] = {
                "level": game_data.player.fighter.shield.level,
                "max_level": game_data.player.fighter.shield.max_level,
            }
        else:
            data["shield"] = None
        return data

    data = {
        "seed": seed,
        "config": config.conf.serialize(),
        "messages": [msg.text for msg in game_data.log.messages] if game_data else ["no game_data"],
        "input_events": input_recorder.serialize_input(input_recorder.events),
        "crashed": crashed,
        "end_state": serialize_end_state(),
        "events" : game_data.logger.serialize()
    }
    timestamp = start_time.strftime("%Y-%m-%d_%H-%M-%S")
    if crashed:
        data["traceback"] = str(traceback.format_exc())
        logname = "formula_run.{}.crash.log".format(timestamp)
    else:
        logname = "formula_run.{}.log".format(timestamp)
    dirname = "formula_logs"
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    path = os.path.abspath((os.path.join(dirname, logname)))
    with open(path, "w") as writer:
        writer.write(serialization.serialize(data, indent=2))

    print("Log file {} written".format(path))


def load_replay_log(path):
    with open(path, "r") as reader:
        content = reader.read()
    data = AttrDict(json.loads(content))

    config.conf.random_seed = data.seed

    if "unlock_mode" in data.config:
        config.conf.unlock_mode = data.config.unlock_mode
    if "cooldown_mode" in data.config:
        config.conf.cooldown_mode = data.config.cooldown_mode
    if "starting_mode" in data.config:
        config.conf.starting_mode = data.config.starting_mode
    if "keys" in data.config:
        config.conf.keys = data.config["keys"]
    if "pickup" in data.config:
        config.conf.pickup = data.config.pickup
    if "pickupstartcount" in data.config:
        config.conf.pickupstartcount = data.config.pickupstartcount
    if "crafting" in data.config:
        config.conf.crafting = data.config.crafting
    if "consumables" in data.config:
        config.conf.consumables = data.config.consumables
    if "trap" in data.config:
        config.conf.trap = data.config.trap
    if "trapcast" in data.config:
        config.conf.trapcast = data.config.trapcast
    if "heal" in data.config:
        config.conf.heal = data.config.heal

    events = data.input_events
    deserialized = input_recorder.deserialize_input(events)
    input_recorder.events.extend(deserialized)


def write_profiling_data(starting_time, profiler):
    timestamp = starting_time.strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.abspath(f"formula.profiling.{timestamp}.data")
    profiler.dump_stats(path)
    print(f"Profiling data written at {path}")


def main():

    if config.conf.stats:
        balance_statistics.print_stats()
        return

    profiler = None
    if config.conf.profiling:
        import cProfile

        profiler = cProfile.Profile()
        profiler.enable()

    if config.conf.is_replaying:
        load_replay_log(config.conf.replay_log_path)

    game_data = None
    now = datetime.datetime.now()
    seed = set_seed()

    try:
        constants = get_constants()
        game_data, gfx_data = do_setup(constants)

        now = datetime.datetime.now()
        while play_game(game_data, gfx_data):
            game_data, gfx_data = do_setup(constants, previous_data=game_data)

        if config.conf.profiling:
            profiler.disable()
            write_profiling_data(now, profiler)

        pygame.quit()

        if config.conf.is_testing:
            tester.validate_state(game_data, config.conf.test_data)
        elif not config.conf.is_replaying:
            write_logs(game_data, seed, now, crashed=False)

    except:
        traceback.print_exc()
        try:
            write_logs(game_data, seed, now, crashed=True)
        except:
            print("Failed to write crashlog:")
            traceback.print_exc()


if __name__ == "__main__":
    main()
