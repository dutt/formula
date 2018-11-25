from random import randint

import tcod

from components.action import MoveToTargetAction, AttackAction
from messages import Message


class BasicMonster:
    def take_turn(self, game_data, gfx_data):
        monster = self.owner
        if not tcod.map_is_in_fov(game_data.fov_map, monster.pos.x, monster.pos.y):
            return None
        if monster.distance_to(game_data.player) >= 2:
            return MoveToTargetAction(monster, target=game_data.player).execute(game_data)
        elif game_data.player.fighter.hp > 0:
            gfx_data.visuals.add_temporary(monster.pos, game_data.player.pos, lifespan=0.25,
                                 asset=gfx_data.assets.sword)
            return AttackAction(monster, target=game_data.player).execute(game_data)
        return None


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns
        self.owner = None

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            destx = self.owner.x + randint(0, 2) - 1
            desty = self.owner.y + randint(0, 2) - 1

            if destx != self.owner.x and desty != self.owner.y:
                self.owner.move_towards(destx, desty, game_map, entities)
            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({"message": Message("The {} is no longer confused".format(self.owner.name))})

        return results
