import datetime

import tcod

from components.drawable import Drawable
from components.game_states import GameStates
from graphics.render_order import RenderOrder
from systems.messages import Message


def kill_player(game_state, assets):
    game_state.player.drawable = Drawable(assets.monster_corpse)
    game_state.player.render_order = RenderOrder.CORPSE
    game_state.player.name = "Your corpse"
    game_state.state = GameStates.PLAYER_DEAD
    game_state.stats.end_time = datetime.datetime.now()
    return Message("You died", tcod.red), game_state


def kill_monster(monster, game_state, assets):
    msg = Message("{} is dead".format(monster.name), tcod.orange)

    monster.drawable = Drawable(assets.monster_corpse)
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.render_order = RenderOrder.CORPSE
    monster.name = "Remains of {}".format(monster.name)
    monster.active = False
    game_state.timesystem.release(monster)

    return msg, game_state
