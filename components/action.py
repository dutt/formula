from attrdict import AttrDict as attrdict


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


class MoveAction(Action):
    COST = 100

    def __init__(self, actor, target=None, targetpos=None):
        super(MoveAction, self).__init__(actor, MoveAction.COST)
        assert target is not None or targetpos is not None
        self.targetpos = targetpos
        self.target = target

    def execute(self, game_data):
        def helper(x, y):
            self.actor.move_towards(x, y, game_data.map, game_data.entities)
            return [{"moved": True}]

        if self.target:
            result = helper(self.target.pos.x, self.target.pos.y)
        else:
            result = helper(self.targetpos.x, self.targetpos.y)
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
