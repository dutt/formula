import tcod

import gfx
from game_states import GameState
from messages import Message


def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red
    player.render_order = gfx.RenderOrder.CORPSE
    player.name = "Your corpse"

    return Message("You died", tcod.red), GameState.PLAYER_DEAD


def kill_monster(monster):
    msg = Message("{} is dead".format(monster.name), tcod.orange)

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.render_order = gfx.RenderOrder.CORPSE
    monster.name = "Remains of {}".format(monster.name)

    return msg
