from attrdict import AttrDict as attrdict

from components.game_states import GameStates
from systems.fov import initialize_fov
from systems.messages import Message
import config


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


class LootAction(Action):
    def __init__(self, actor):
        super().__init__(actor=actor, cost=100)

    def execute(self, game_data, gfx_data):
        import random

        val = random.randint(0, 100)
        if val <= 40:
            game_data.player.fighter.heal(3)
            result = [
                {
                    "message": Message(
                        "You found a healing potion and has been healed 3 points"
                    )
                }
            ]
            return self.package(result=result)
        elif val <= 70:
            shield = game_data.player.fighter.shield
            shield_strength = 3
            if shield:
                shield.level += shield_strength
                if shield.level > shield.max_level:
                    shield.max_level = shield.level
                text = "You found a jewel, when you touch it your shield strengthens"
            else:
                from components.effects import EffectBuilder, EffectType

                shield_effect = EffectBuilder.create(
                    EffectType.DEFENSE,
                    level=shield_strength,
                    strikebacks=[],
                    distance=0,
                )
                shield_effect.apply(game_data.player)
                text = (
                    "You found a jewel, when you touch it a shield appears around you"
                )
            result = [{"message": Message(text)}]
            return self.package(result=result)
        else:
            cooldown_reduction = 5
            for _ in range(0, cooldown_reduction):
                game_data.player.caster.tick_cooldowns()
            text = "You found a jewel, when you touch it you shimmer, cooldowns reduced by {}".format(
                cooldown_reduction
            )
            result = [{"message": Message(text)}]
            return self.package(result=result)


class ExitAction(Action):
    def __init__(self, keep_playing, ask=True):
        super(ExitAction, self).__init__(actor=None, cost=1000)
        self.keep_playing = keep_playing
        self.ask = ask

    def execute(self, game_data, gfx_data):
        if game_data.state == GameStates.PLAY and self.ask:
            game_data.prev_state.append(game_data.state)
            game_data.state = GameStates.ASK_QUIT
            gfx_data.windows.activate_wnd_for_state(game_data.state)
        else:
            return self.package(
                result=[{"quit": True, "keep_playing": self.keep_playing}]
            )


class WaitAction(Action):
    COST = 100

    def __init__(self, actor):
        super(WaitAction, self).__init__(actor=actor, cost=WaitAction.COST)

    def execute(self, game_data, gfx_data):
        return self.package()


class DescendStairsAction(Action):
    COST = 100

    def __init__(self, actor):
        super(DescendStairsAction, self).__init__(
            actor=actor, cost=DescendStairsAction.COST
        )

    def execute(self, game_data, gfx_data):
        all_crystals = (
            game_data.map.num_crystals_found == game_data.map.num_crystals_total
        )
        if not all_crystals:
            num_remaining = (
                game_data.map.num_crystals_total - game_data.map.num_crystals_found
            )
            text = "You haven't found all the keys on this level yet, {} keys left".format(
                num_remaining
            )
            result = [{"message": Message(text)}]
            return self.package(result=result)

        if game_data.run_planner.has_next:
            if config.conf.keys == "keys":
                game_data.player.level.add_xp(game_data.player.level.xp_to_next_level)

            game_data.prev_state.append(game_data.state)
            game_data.prev_state.append(GameStates.STORY_SCREEN)
            game_data.state = GameStates.FORMULA_SCREEN
            game_data.map = game_data.run_planner.activate_next_level()
            game_data.map.entities = game_data.map.entities
            game_data.fov_map = initialize_fov(game_data.map)
            game_data.fov_recompute = True
            from graphics.camera import Camera

            cam_width = min(game_data.map.width, gfx_data.camera.orig_width)
            cam_height = min(game_data.map.height, gfx_data.camera.orig_height)
            gfx_data.camera = Camera(cam_width, cam_height, game_data)
            gfx_data.windows.activate_wnd_for_state(game_data.state)
            game_data.stats.next_level()
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
        if game_data.player.pos != self.targetpos:
            self.actor.move_towards(
                self.targetpos.x,
                self.targetpos.y,
                game_data.map.entities,
                game_data.map,
            )
        result = [{"moved": True}]
        return self.package(result)


class MoveToTargetAction(Action):
    COST = 100

    def __init__(self, actor, target):
        super(MoveToTargetAction, self).__init__(actor, MoveToTargetAction.COST)
        self.target = target

    def execute(self, game_data, _):
        self.actor.move_astar(self.target.pos, game_data.map.entities, game_data.map)
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
        result = self.formula.apply(
            entities=game_data.map.entities,
            fov_map=game_data.fov_map,
            caster=self.actor,
            target_x=self.targetpos.x,
            target_y=self.targetpos.y,
        )
        return self.package(result)


class PickupCrystalAction(Action):
    COST = 100

    def __init__(self, actor, crystal_entity):
        super(PickupCrystalAction, self).__init__(actor, PickupCrystalAction.COST)
        self.crystal = crystal_entity

    def execute(self, game_data, gfx_data):
        game_data.map.entities.remove(self.crystal)
        game_data.map.num_crystals_found += 1
        if game_data.map.num_crystals_found == game_data.map.num_crystals_total:
            text = "All keys found, head to the stairs"
        else:
            text = "You found a key, {}/{} keys found".format(
                game_data.map.num_crystals_found, game_data.map.num_crystals_total
            )
        result = [{"message": Message(text)}]
        return self.package(result=result)
