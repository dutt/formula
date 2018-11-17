from attrdict import AttrDict as attrdict

from game_states import GameStates
from fov import initialize_fov

class Action:
    def __init__(self, actor, cost):
        self.actor = actor
        self.cost = cost

    def package(self, result=[]):
        if result:
            return attrdict({"result": result, "action": self})
        else:
            return None


class ExitAction(Action):
    def __init__(self):
        super(ExitAction, self).__init__(actor=None, cost=1000)

    def execute(self, _):
        return self.package(result=[{"quit": True}])


class WaitAction(Action):
    COST = 100

    def __init__(self, actor):
        super(WaitAction, self).__init__(actor=actor, cost=WaitAction.COST)

    def execute(self, _):
        return self.package()

class DescendStairsAction(Action):
    COST = 100

    def __init__(self, actor):
        super(DescendStairsAction, self).__init__(actor=actor, cost=DescendStairsAction.COST)

    def execute(self, game_data):
        game_data.entities = game_data.map.next_floor(game_data.player, game_data.log,
                                                      game_data.constants,
                                                      game_data.entities, game_data.timesystem)
        game_data.prev_state = [GameStates.PLAY]
        game_data.state = GameStates.SPELLMAKER_SCREEN
        game_data.fov_map = initialize_fov(game_data.map)
        game_data.fov_recompute = True
        result = [{"descended" : True}]
        return self.package(result)

class MoveToPositionAction(Action):
    COST = 100

    def __init__(self, actor, targetpos):
        super(MoveToPositionAction, self).__init__(actor, MoveToTargetAction.COST)
        self.targetpos = targetpos

    def execute(self, game_data):
        self.actor.move_towards(self.targetpos.x, self.targetpos.y, game_data.entities, game_data.map)
        result = [{"moved": True}]
        return self.package(result)


class MoveToTargetAction(Action):
    COST = 100

    def __init__(self, actor, target):
        super(MoveToTargetAction, self).__init__(actor, MoveToTargetAction.COST)
        self.target = target

    def execute(self, game_data):
        self.actor.move_astar(self.target, game_data.entities, game_data.map)
        result = [{"moved": True}]
        return self.package(result)


class AttackAction(Action):
    COST = 100

    def __init__(self, actor, target):
        super(AttackAction, self).__init__(actor, AttackAction.COST)
        self.target = target

    def execute(self, game_data):
        result = self.actor.fighter.attack(self.target)
        return self.package(result)


class CastSpellAction(Action):
    COST = 100

    def __init__(self, actor, spell, targetpos):
        super(CastSpellAction, self).__init__(actor, CastSpellAction.COST)
        self.spell = spell
        self.targetpos = targetpos

    def execute(self, game_data):
        result = self.spell.apply(entities=game_data.entities,
                                  fov_map=game_data.fov_map, caster=self.actor,
                                  target_x=self.targetpos.x, target_y=self.targetpos.y)
        return self.package(result)