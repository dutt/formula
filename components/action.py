from attrdict import AttrDict as attrdict


class Action:
    def __init__(self, actor, cost):
        self.actor = actor
        self.cost = cost

    def package(self, result):
        if result:
            return attrdict({"result": result, "action": self})
        else:
            return None

class DecendStairsAction(Action):
    COST = 0 #new map, reset
    def __init__(self):
        super(DecendStairsAction, self).__init__(self, 0)

class MoveAction(Action):
    COST = 100

    def __init__(self, actor, target=None, targetpos=None):
        super(MoveAction, self).__init__(actor, MoveAction.COST)
        assert target is not None or targetpos is not None
        self.targetpos = targetpos
        self.target = target

    def execute(self, game_data):
        def helper(x, y):
            return self.actor.move_towards(x, y, game_data.map, game_data.entities)
        if self.target:
            helper(self.target.pos.x, self.target.pos.y)
        else:
            helper(self.targetpos.x, self.targetpos.y)
        return self.package(result="moved")


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

    def __init__(self, actor, spell, targetpos, target):
        super(CastSpellAction, self).__init__(actor, CastSpellAction.COST)
        self.spell = spell
        self.target = target
        self.targetpos = targetpos

    def execute(self, game_data):
        result = self.spell.apply(self, self.targetpos, self.target)
        return self.package(result)
