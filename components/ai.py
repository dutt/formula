from random import randint

import tcod

from messages import Message

class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        monster = self.owner
        results = []
        if not tcod.map_is_in_fov(fov_map, monster.x, monster.y):
            return results
        if monster.distance_to(target) >= 2:
            monster.move_astar(target, entities, game_map)
        elif target.fighter.hp > 0:
            results.extend(monster.fighter.attack(target))
        return results

class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

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
            results.append({"message" : Message("The {} is no longer confused".format(self.owner.name))})

        return results