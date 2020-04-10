import random
import datetime

from attrdict import AttrDict as attrdict

from components.game_states import GameStates
from systems.fov import initialize_fov
from systems.messages import Message
import config
from components.effects import EffectBuilder, EffectType
from graphics.camera import Camera


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


def do_looting(game_data, gfx_data, prefix):
    val = random.randint(0, 100)
    can_heal = game_data.player.fighter.hp < game_data.player.fighter.max_hp
    if val <= 40 and can_heal:
        amount = 3
        game_data.player.fighter.heal(amount)
        result = [{"message": Message(f"{prefix} your wounds close, you've been healed {amount} points")}]
    elif val <= 70 and game_data.player.caster.has_cooldown():
        cooldown_reduction = 5
        for _ in range(0, cooldown_reduction):
            game_data.player.caster.tick_cooldowns()
        text = f"{prefix} you shimmer, cooldowns reduced by {cooldown_reduction}"
        result = [{"message": Message(text)}]
    else: # we can always add more shield
        shield = game_data.player.fighter.shield
        shield_strength = 3
        if shield:
            shield.level += shield_strength
            if shield.level > shield.max_level:
                shield.max_level = shield.level
            text = f"{prefix} your shield strengthens"
        else:
            shield_effect = EffectBuilder.create(EffectType.DEFENSE, level=shield_strength, strikebacks=[], distance=0,)
            shield_effect.apply(game_data.player)
            text = f"{prefix} a shield appears around you"
        result = [{"message": Message(text)}]
    return result


class LootAction(Action):
    def __init__(self, actor):
        super().__init__(actor=actor, cost=100)

    def execute(self, game_data, gfx_data):
        return self.package(result=do_looting(game_data, gfx_data, prefix="You found a jewel, when you touch it"))


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
            return self.package(result=[{"quit": True, "keep_playing": self.keep_playing}])


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
        all_keys = game_data.map.num_keys_found == game_data.map.num_keys_total
        if not all_keys:
            num_remaining = game_data.map.num_keys_total - game_data.map.num_keys_found
            text = "You haven't found all the keys on this level yet, {} keys left".format(num_remaining)
            game_data.map.stairs_found = True
            result = [{"message": Message(text)}]
            return self.package(result=result)

        if game_data.run_planner.has_next:

            if game_data.map.tutorial:
                # re-set formulas after tutorial
                game_data.formula_builder.run_tutorial = False
                game_data.formula_builder.set_initial_slots()
                game_data.player.caster.clear_cooldowns()
            elif config.conf.keys:
                game_data.player.level.add_xp(game_data.player.level.xp_to_next_level)

            game_data.prev_state.append(game_data.state)
            game_data.prev_state.append(GameStates.FORMULA_SCREEN)
            game_data.state = GameStates.STORY_SCREEN
            game_data.map = game_data.run_planner.activate_next_level()
            game_data.map.entities = game_data.map.entities
            game_data.fov_map = initialize_fov(game_data.map)
            game_data.fov_recompute = True

            cam_width = min(game_data.map.width, gfx_data.camera.orig_width)
            cam_height = min(game_data.map.height, gfx_data.camera.orig_height)
            gfx_data.camera = Camera(cam_width, cam_height, game_data)
            gfx_data.windows.activate_wnd_for_state(game_data.state)
            gfx_data.camera.initialize_map()
            gfx_data.camera.center_on(game_data.player.pos.x, game_data.player.pos.y)
            game_data.stats.next_level()
            result = [{"descended": True}]
        else:
            game_data.prev_state.append(game_data.state)
            game_data.state = GameStates.VICTORY
            game_data.story.next_story()
            gfx_data.windows.activate_wnd_for_state(game_data.state)
            game_data.stats.end_time = datetime.datetime.now()
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
                self.targetpos.x, self.targetpos.y, game_data.map.entities, game_data.map,
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


class PickupKeyAction(Action):
    COST = 100

    def __init__(self, actor, key_entity):
        super(PickupKeyAction, self).__init__(actor, PickupKeyAction.COST)
        self.key = key_entity

    def execute(self, game_data, gfx_data):
        game_data.map.entities.remove(self.key)
        game_data.map.num_keys_found += 1
        if game_data.map.num_keys_found == game_data.map.num_keys_total:
            text = "All keys found, head to the stairs"
        elif game_data.map.stairs_found:
            text = "You found a key, {}/{} keys found".format(
                game_data.map.num_keys_found, game_data.map.num_keys_total
            )
        else:
            text = "You found a key, {} keys found, wonder how many are left?".format(game_data.map.num_keys_found)
        result = [{"message": Message(text)}]
        result.extend(do_looting(game_data, gfx_data, prefix="You pick up the key and"))
        return self.package(result=result)
