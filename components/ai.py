from components.action import MoveToTargetAction, AttackAction, WaitAction
from components.verbs import can_attack_player, can_move_towards_player


class DummyMonsterAI:
    def take_turn(self, game_data, gfx_data):
        monster = self.owner
        return WaitAction(monster).execute(game_data, gfx_data)


class MeleeMonsterAI:
    def take_turn(self, game_data, gfx_data):
        monster = self.owner
        if can_move_towards_player(monster, game_data):
            return MoveToTargetAction(monster, target=game_data.player).execute(game_data, gfx_data)
        elif can_attack_player(monster, game_data):
            gfx_data.visuals.add_temporary(
                monster.pos, game_data.player.pos, lifespan=0.2, asset=gfx_data.assets.sword,
            )
            return AttackAction(monster, target=game_data.player).execute(game_data, gfx_data)
        else:
            return WaitAction(monster).execute(game_data, gfx_data)


class RangedMonsterAI:
    def take_turn(self, game_data, gfx_data):
        monster = self.owner
        if can_attack_player(monster, game_data, max_dist=monster.range):
            gfx_data.visuals.add_temporary(
                monster.pos, game_data.player.pos, lifespan=0.2, asset=gfx_data.assets.arrow,
            )
            return AttackAction(monster, target=game_data.player).execute(game_data, gfx_data)
        elif can_move_towards_player(monster, game_data):
            return MoveToTargetAction(monster, target=game_data.player).execute(game_data, gfx_data)
        else:
            return WaitAction(monster).execute(game_data, gfx_data)
