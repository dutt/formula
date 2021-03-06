import datetime
import time

import pygame
import tcod

from components.action import (
    MoveToPositionAction,
    AttackAction,
    ExitAction,
    ThrowVialAction,
    WaitAction,
    DescendStairsAction,
    LootAction,
    PickupKeyAction,
    PickupIngredientAction,
    UseConsumableAction,
    PickupConsumableAction,
)
from components.caster import Caster
from components.drawable import Drawable
from components.fighter import Fighter
from components.level import Level
from components.entity import Entity, get_blocking_entites_at_location
from systems.fov import recompute_fov
from components.game_states import GameStates
from graphics.assets import Assets
from graphics.render_order import RenderOrder
from systems.input_handlers import EventType, handle_keys, handle_mouse
from systems.messages import Message
from systems import input_recorder
from components.events import InputType, KeyEvent, MouseEvent
from util import Pos, Vec
from graphics.level_up_window import LevelUpWindow
import config


class Player(Entity):
    def __init__(self, godmode):
        caster_component = Caster(num_slots=3, num_formulas=3)
        if godmode:
            fighter_component = Fighter(hp=10, defense=50, power=50)
        else:
            fighter_component = Fighter(hp=10, defense=0, power=3)

        level_component = Level()
        drawable_component = Drawable(Assets.get().player)

        super(Player, self).__init__(
            x=0,
            y=0,
            name="You",
            speed=100,
            blocks=True,
            render_order=RenderOrder.ACTOR,
            fighter=fighter_component,
            level=level_component,
            caster=caster_component,
            drawable=drawable_component,
        )
        self.last_num_explored = None
        self.moving_towards = None
        self.godmode = godmode
        self.ignore_first_click = False

    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value):
        self.name_ = value

    @property
    def name_with_prep(self):
        return "You are"

    def handle_tick_cooldowns(self, game_data):
        if config.conf.cooldown_mode == "always":
            self.caster.tick_cooldowns()
        elif config.conf.cooldown_mode == "unary":
            if game_data.map.num_explored > self.last_num_explored:
                self.caster.tick_cooldowns()
                self.last_num_explored = game_data.map.num_explored
        elif config.conf.cooldown_mode == "counting":
            if game_data.map.num_explored > self.last_num_explored:
                diff = game_data.map.num_explored - self.last_num_explored
                for _ in range(diff):
                    self.caster.tick_cooldowns()
                self.last_num_explored = game_data.map.num_explored

    def take_turn(self, game_data, gfx_data):
        def handle_fullscreen(fullscreen):
            display = (
                game_data.constants.window_size.width,
                game_data.constants.window_size.height,
            )
            if pygame.display.get_driver() == "x11":
                pygame.display.toggle_fullscreen()
            else:
                display_copy = gfx_data.main.copy()
                if fullscreen:
                    gfx_data.main = pygame.display.set_mode(display)
                else:
                    gfx_data.main = pygame.display.set_mode(display, pygame.FULLSCREEN)
                    gfx_data.fullscreen = not gfx_data.fullscreen
                    gfx_data.main.blit(display_copy, (0, 0))
                    pygame.display.update()

        def handle_interact(turn_results):
            player_action = None

            for e in game_data.map.entities:
                if e.pos.x == self.pos.x and e.pos.y == self.pos.y:
                    if e.stairs:
                        self.last_num_explored = None
                        game_data.story.next_story()
                        self.caster.clear_cooldowns()
                        player_action = DescendStairsAction(self)
                        break
                    elif e.key:
                        player_action = PickupKeyAction(self, e)
                        break
                    elif e.ingredient:
                        player_action = PickupIngredientAction(self, e)
                        break
                    elif e.consumable:
                        player_action = PickupConsumableAction(self, e)
                        break
                    elif e.name.startswith("Remains of"):  # monster
                        if e.orig_name == "Arina":
                            game_data.prev_state.append(game_data.state)
                            game_data.state = GameStates.VICTORY
                            game_data.story.next_story()
                            gfx_data.windows.activate_wnd_for_state(game_data.state, game_data, gfx_data)
                            game_data.stats.end_time = datetime.datetime.now()
                        elif not config.conf.keys:
                            e.name = "Looted r" + e.name[1:]
                            game_data.stats.loot_monster(e)
                            player_action = LootAction(self)
                        break
            else:
                if config.conf.cooldown_mode != "always":
                    player_action = WaitAction(self)
            return player_action, turn_results

        def handle_show_help():
            game_data.prev_state.append(game_data.state)
            if game_data.state == GameStates.FORMULA_SCREEN:
                game_data.state = GameStates.FORMULA_HELP_SCEEN
            elif game_data.state == GameStates.STORY_SCREEN:
                game_data.state = GameStates.STORY_HELP_SCREEN
            elif game_data.state == GameStates.INVENTORY:
                game_data.state = GameStates.INVENTORY_HELP
            elif game_data.state == GameStates.CRAFTING:
                game_data.state = GameStates.CRAFTING_HELP
            else:
                game_data.state = GameStates.GENERAL_HELP_SCREEN
            gfx_data.windows.activate_wnd_for_state(game_data.state, game_data, gfx_data)

        def handle_move(move, turn_results):
            player_action = None

            dx, dy = move
            destx = self.pos.x + dx
            desty = self.pos.y + dy

            if self.godmode:
                self.pos = Pos(destx, desty)
                gfx_data.camera.center_on(destx, desty)
                game_data.stats.move_player(Pos(destx, desty))
                player_action = MoveToPositionAction(self, targetpos=Pos(destx, desty))
            elif not game_data.map.is_blocked(destx, desty):
                target = get_blocking_entites_at_location(game_data.map.entities, destx, desty)
                if target and target.fighter:
                    player_action = AttackAction(self, target=target)
                else:
                    gfx_data.camera.center_on(destx, desty)
                    game_data.stats.move_player(Pos(destx, desty))
                    player_action = MoveToPositionAction(self, targetpos=Pos(destx, desty))
            return player_action, turn_results

        def handle_moving_towards(turn_results):
            player_action = None
            if self.pos == self.moving_towards:
                self.moving_towards = None
            else:
                last_moving_towards_pos = Pos(self.pos.x, self.pos.y)
                self.move_astar(
                    self.moving_towards, game_data.map.entities, game_data.map, length_limit=False,
                )
                if last_moving_towards_pos == self.pos:
                    self.moving_towards = None
                else:
                    gfx_data.camera.center_on(self.pos.x, self.pos.y)
                    game_data.stats.move_player(self.pos)
                    time.sleep(0.15)
                    player_action = MoveToPositionAction(self, targetpos=Pos(self.pos.x, self.pos.y))
            return player_action, turn_results

        def handle_start_throwing_vial(start_throwing_vial, turn_results):
            player_action = None
            if start_throwing_vial >= len(self.caster.formulas):
                game_data.log.add_message(Message("You don't have that formula yet", tcod.yellow))
            elif self.caster.is_on_cooldown(start_throwing_vial):
                game_data.log.add_message(Message("That's not ready yet", tcod.yellow))
            else:
                formula = self.caster.formulas[start_throwing_vial]
                if formula.targeted:
                    start_throwing_vial_results = {
                        "targeting_formula": formula,
                        "formula_idx": start_throwing_vial,
                    }
                    turn_results.append(start_throwing_vial_results)
                else:
                    player_action = ThrowVialAction(self, formula, targetpos=game_data.player.pos)
            return player_action, turn_results

        def handle_use_consumable(use_consumable, turn_results):
            player_action = None
            item = game_data.inventory.get_quickslot(use_consumable)
            if item:
                if item.targeted:
                    res = {
                        "use_consumable": item,
                        "use_consumable_index": use_consumable,
                    }
                    turn_results.append(res)
                else:
                    player_action = UseConsumableAction(self, item, targetpos=game_data.player.pos)
            return player_action, turn_results

        def handle_targeting(left_click, right_click, turn_results):
            player_action = None
            if left_click:
                targetx, targety = left_click.cx, left_click.cy
                distance = (self.pos - Vec(targetx, targety)).length()
                if game_data.targeting_formula:

                    alternate = left_click.alternate
                    if alternate and config.conf.trapcast:
                        game_data.targeting_formula.trap = True
                        game_data.targeting_formula.set_texts()

                    if distance > game_data.targeting_formula.distance:
                        turn_results.append(
                            {"target_out_of_range": True, "targeting_formula": game_data.targeting_formula,}
                        )
                    else:
                        player_action = ThrowVialAction(
                            self, game_data.targeting_formula, targetpos=(Pos(targetx, targety)),
                        )
                        # gfx_data.visuals.add_temporary(self.pos, Pos(targetx, targety), lifespan=distance * 0.1,
                        gfx_data.visuals.add_temporary(
                            self.pos, Pos(targetx, targety), lifespan=0.2, asset=gfx_data.assets.throwing_bottle,
                        )
                        game_data.state = game_data.prev_state.pop()
                        game_data.targeting_formula_idx = None
                elif game_data.targeting_consumable:
                    if distance > game_data.targeting_consumable.distance:
                        turn_results.append(
                            {"target_out_of_range": True, "targeting_consumable": game_data.targeting_consumable,}
                        )
                    else:
                        player_action = UseConsumableAction(
                            self, game_data.targeting_consumable, targetpos=(Pos(targetx, targety)),
                        )
                        gfx_data.visuals.add_temporary(
                            self.pos, Pos(targetx, targety), lifespan=0.2, asset=gfx_data.assets.throwing_bottle,
                        )
                        game_data.state = game_data.prev_state.pop()
                        game_data.targeting_consumable = None

            elif right_click:
                turn_results.append({"targeting_cancelled": True})
            return player_action, turn_results

        if game_data.stats.start_time is None:
            game_data.stats.start_time = datetime.datetime.now()

        if self.action_points < 100:
            return None

        player_action = None
        if not self.last_num_explored:
            recompute_fov(
                game_data.fov_map,
                game_data.player.pos.x,
                game_data.player.pos.y,
                game_data.constants.fov_radius,
                game_data.constants.fov_light_walls,
                game_data.constants.fov_algorithm,
            )
            self.last_num_explored = game_data.map.num_explored
        self.handle_tick_cooldowns(game_data)

        while not player_action:

            turn_results = []

            if game_data.fov_recompute:
                recompute_fov(
                    game_data.fov_map,
                    game_data.player.pos.x,
                    game_data.player.pos.y,
                    game_data.constants.fov_radius,
                    game_data.constants.fov_light_walls,
                    game_data.constants.fov_algorithm,
                )
            gfx_data.windows.draw(game_data, gfx_data)

            events = pygame.event.get()
            quit_events = [e for e in events if e.type == pygame.QUIT]
            if quit_events:
                player_action = ExitAction(keep_playing=False, ask=False)

            if config.conf.is_replaying and input_recorder.events:
                if not config.conf.is_testing:
                    time.sleep(0.2)
                next_event = input_recorder.events.pop(0)
                print(f"Replaying event {next_event}")
                if next_event.event_type == InputType.KEY:
                    key_events = [next_event]
                    mouse_events = []
                else:
                    key_events = []
                    mouse_events = [next_event]
            else:
                if not pygame.key.get_focused() and not self.ignore_first_click:
                    self.ignore_first_click = True

                key_events = [KeyEvent(e) for e in events if e.type == pygame.KEYDOWN]
                mouse_events = [MouseEvent(e) for e in events if e.type == pygame.MOUSEBUTTONDOWN]

                if key_events and self.ignore_first_click:
                    self.ignore_first_click = False

            key_action = handle_keys(key_events, game_data.state)
            mouse_action = handle_mouse(mouse_events, game_data.constants, gfx_data.camera, self.ignore_first_click, game_data.logger)

            if mouse_action:
                if self.ignore_first_click:
                    self.ignore_first_click = False
                else:
                    gui_action = gfx_data.windows.handle_click(game_data, gfx_data, mouse_action)
                    if gui_action:
                        mouse_action = gui_action

            if key_action:
                handled, gui_action = gfx_data.windows.handle_key(game_data, gfx_data, key_action)
                if handled:
                    key_action = gui_action

            fullscreen = key_action.get(EventType.fullscreen)
            move = key_action.get(EventType.move)
            do_exit = key_action.get(EventType.exit)
            left_click = mouse_action.get(EventType.left_click)
            right_click = mouse_action.get(EventType.right_click)
            show_help = key_action.get(EventType.show_help)
            interact = key_action.get(EventType.interact)
            start_crafting = key_action.get(EventType.start_crafting)
            inventory = key_action.get(EventType.inventory)

            use_consumable = None
            if key_action.get(EventType.use_consumable) is not None:
                use_consumable = key_action.get(EventType.use_consumable)
            elif mouse_action.get(EventType.use_consumable) is not None:
                use_consumable = mouse_action.get(EventType.use_consumable)

            start_throwing_vial = None
            if key_action.get(EventType.start_throwing_vial) is not None:
                start_throwing_vial = key_action.get(EventType.start_throwing_vial)
            elif mouse_action.get(EventType.start_throwing_vial) is not None:
                start_throwing_vial = mouse_action.get(EventType.start_throwing_vial)

            if interact:
                action, turn_results = handle_interact(turn_results)
                assert turn_results is not None
                if action:
                    player_action = action

            if start_crafting:
                game_data.prev_state.append(game_data.state)
                game_data.state = GameStates.CRAFTING
                gfx_data.windows.activate_wnd_for_state(game_data.state, game_data, gfx_data)

            if inventory:
                game_data.prev_state.append(game_data.state)
                game_data.state = GameStates.INVENTORY
                gfx_data.windows.activate_wnd_for_state(game_data.state, game_data, gfx_data)

            if show_help:
                handle_show_help()

            elif move:
                action, turn_results = handle_move(move, turn_results)
                assert turn_results is not None
                if action:
                    player_action = action

            if left_click and game_data.state == GameStates.PLAY:
                valid_tile = True
                if left_click.cx >= game_data.map.width or left_click.cy >= game_data.map.height:
                    valid_tile = False
                for e in game_data.map.entities:
                    if e.pos.x == left_click.cx and e.pos.y == left_click.cy:
                        if e.ai:
                            valid_tile = False
                if valid_tile and game_data.map.tiles[left_click.cx][left_click.cy].explored:
                    # click to move
                    self.moving_towards = Pos(left_click.cx, left_click.cy)

            if self.moving_towards:
                action, turn_results = handle_moving_towards(turn_results)
                assert turn_results is not None
                if action:
                    player_action = action

            if game_data.state == GameStates.LEVEL_UP:
                gfx_data.windows.get(LevelUpWindow).visible = True

            elif game_data.state == GameStates.TARGETING:
                action, turn_results = handle_targeting(left_click, right_click, turn_results)
                assert turn_results is not None
                if action:
                    player_action = action

            if start_throwing_vial is not None:
                action, turn_results = handle_start_throwing_vial(start_throwing_vial, turn_results)
                assert turn_results is not None
                if action:
                    player_action = action

            if use_consumable is not None:
                action, turn_results = handle_use_consumable(use_consumable, turn_results)
                assert turn_results is not None
                if action:
                    player_action = action

            if do_exit:
                if game_data.state == GameStates.TARGETING:
                    turn_results.append({"targeting_cancelled": True})
                else:
                    keep_playing = key_action.get(EventType.keep_playing)
                    player_action = ExitAction(keep_playing)

            if fullscreen:
                handle_fullscreen(fullscreen)

            key_action = mouse_action = None  # clear them for next round

            for res in turn_results:
                game_data.targeting_formula = res.get("targeting_formula")
                game_data.targeting_formula_idx = res.get("formula_idx")
                if game_data.targeting_formula:
                    formula_idx = res.get("formula_idx")
                    if self.caster.is_on_cooldown(formula_idx):
                        game_data.log.add_message(self.caster.cooldown_message)
                    else:
                        game_data.prev_state.append(game_data.state)
                        game_data.state = GameStates.TARGETING
                        game_data.log.add_message(game_data.targeting_formula.targeting_message)

                targeting_cancelled = res.get("targeting_cancelled")
                if targeting_cancelled:
                    game_data.state = game_data.prev_state.pop()
                    game_data.log.add_message(Message("Targeting cancelled"))

                target_out_of_range = res.get("target_out_of_range")
                if target_out_of_range:
                    game_data.log.add_message(Message("Target out of range"))

                use_consumable = res.get(EventType.use_consumable)
                if use_consumable:
                    if use_consumable.targeted:
                        game_data.targeting_consumable = use_consumable
                        print(f"{use_consumable.name} is a targeted consumable, targeting...")
                        game_data.prev_state.append(game_data.state)
                        game_data.state = GameStates.TARGETING

            gfx_data.visuals.update(game_data, gfx_data)
            gfx_data.clock.tick(gfx_data.fps_per_second)
            pygame.display.flip()

        # end of no action
        assert player_action
        if type(player_action) == MoveToPositionAction:
            game_data.fov_recompute = True
        return player_action.execute(game_data, gfx_data)
