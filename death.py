import tcod

import gfx
from game_states import GameStates
from messages import Message


def kill_player(player, game_state):
    game_state.player.char = '%'
    game_state.player.color = tcod.dark_red
    game_state.player.render_order = gfx.RenderOrder.CORPSE
    game_state.player.name = "Your corpse"
    game_state.state = GameStates.PLAYER_DEAD
    return Message("You died", tcod.red), game_state


def kill_monster(monster, game_state):
    msg = Message("{} is dead".format(monster.name), tcod.orange)

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.render_order = gfx.RenderOrder.CORPSE
    monster.name = "Remains of {}".format(monster.name)
    monster.active = False
    game_state.timesystem.release(monster)

    return msg, game_state
