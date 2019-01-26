from attrdict import AttrDict as attrdict

from fov import initialize_fov
from game_states import GameStates


class Action:
    def __init__(self, actor, cost):
        self.actor = actor
        self.cost = cost

    def execute(self, game_data, gfx_data):
        raise NotImplementedError("execute called on raw Action")

    def package(self, result=[]):
        if result:
            return attrdict({"result": result, "action": self})
        else:
            return None


class ExitAction(Action):
    def __init__(self):
        super(ExitAction, self).__init__(actor=None, cost=1000)

    def execute(self, game_data, gfx_data):
        if game_data.state == GameStates.PLAY:
            game_data.prev_state.append(game_data.state)
            game_data.state = GameStates.ASK_QUIT
            gfx_data.windows.activate_wnd_for_state(game_data.state)
        else:
            return self.package(result=[{"quit": True}])


class WaitAction(Action):
    COST = 100

    def __init__(self, actor):
        super(WaitAction, self).__init__(actor=actor, cost=WaitAction.COST)

    def execute(self, game_data, gfx_data):
        return self.package()


class DescendStairsAction(Action):
    COST = 100

    def __init__(self, actor):
        super(DescendStairsAction, self).__init__(actor=actor, cost=DescendStairsAction.COST)

    def execute(self, game_data, gfx_data):
        if game_data.run_planner.has_next:
            game_data.prev_state.append(game_data.state)
            game_data.prev_state.append(GameStates.STORY_SCREEN)
            game_data.state = GameStates.FORMULA_SCREEN
            game_data.map = game_data.run_planner.activate_next_level()
            game_data.map.entities = game_data.map.entities
            game_data.fov_map = initialize_fov(game_data.map)
            game_data.fov_recompute = True
            gfx_data.windows.activate_wnd_for_state(game_data.state)
            result = [{"descended": True}]
        else:
            game_data.state = GameStates.VICTORY
            gfx_data.windows.activate_wnd_for_state(GameStates.STORY_SCREEN)
            result = [{"victory": True}]
        return self.package(result)


class MoveToPositionAction(Action):
    COST = 100

    def __init__(self, actor, targetpos):
        super(MoveToPositionAction, self).__init__(actor, MoveToTargetAction.COST)
        self.targetpos = targetpos

    def execute(self, game_data, _):
        self.actor.move_towards(self.targetpos.x, self.targetpos.y, game_data.map.entities, game_data.map)
        result = [{"moved": True}]
        return self.package(result)


class MoveToTargetAction(Action):
    COST = 100

    def __init__(self, actor, target):
        super(MoveToTargetAction, self).__init__(actor, MoveToTargetAction.COST)
        self.target = target

    def execute(self, game_data, _):
        self.actor.move_astar(self.target, game_data.map.entities, game_data.map)
        result = [{"moved": True}]
        return self.package(result)


class AttackAction(Action):
    COST = 100

    def __init__(self, actor, target):
        super(AttackAction, self).__init__(actor, AttackAction.COST)
        self.target = target

    def execute(self, game_data, _):
        result = self.actor.fighter.attack(self.target)
        return self.package(result)


class ThrowVialAction(Action):
    COST = 100

    def __init__(self, actor, formula, targetpos):
        super(ThrowVialAction, self).__init__(actor, ThrowVialAction.COST)
        self.formula = formula
        self.targetpos = targetpos

    def execute(self, game_data, _):
        result = self.formula.apply(entities=game_data.map.entities,
                                    fov_map=game_data.fov_map, caster=self.actor,
                                    target_x=self.targetpos.x, target_y=self.targetpos.y)
        return self.package(result)
