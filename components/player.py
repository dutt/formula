import pygame
import tcod

from components.action import MoveToPositionAction, AttackAction, ExitAction, ThrowVialAction, WaitAction, \
    DescendStairsAction, LootAction
from components.caster import Caster
from components.drawable import Drawable
from components.fighter import Fighter
from components.level import Level
from entity import Entity, get_blocking_entites_at_location
from fov import recompute_fov
from game_states import GameStates
from graphics.assets import Assets
from graphics.render_order import RenderOrder
from input_handlers import Event, handle_keys, handle_mouse
from messages import Message
from util import Pos
from graphics.level_up_window import LevelUpWindow
import config

class Player(Entity):
    def __init__(self):
        caster_component = Caster(num_slots=3, num_formulas=3)
        fighter_component = Fighter(hp=1, defense=60, power=300)
        level_component = Level()
        drawable_component = Drawable(Assets.get().player)
        super(Player, self).__init__(0, 0, "You", speed=100, blocks=True,
                                     render_order=RenderOrder.ACTOR,
                                     fighter=fighter_component, level=level_component, caster=caster_component,
                                     drawable=drawable_component)
        self.last_num_explored = None

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

        if self.action_points < 100:
            return None

        player_action = None
        if not self.last_num_explored:
            recompute_fov(game_data.fov_map, game_data.player.pos.x, game_data.player.pos.y,
                          game_data.constants.fov_radius, game_data.constants.fov_light_walls,
                          game_data.constants.fov_algorithm)
            self.last_num_explored = game_data.map.num_explored
        self.handle_tick_cooldowns(game_data)

        while not player_action:

            turn_results = []

            if game_data.fov_recompute:
                recompute_fov(game_data.fov_map, game_data.player.pos.x, game_data.player.pos.y,
                              game_data.constants.fov_radius, game_data.constants.fov_light_walls,
                              game_data.constants.fov_algorithm)
            gfx_data.windows.draw(game_data, gfx_data)

            events = pygame.event.get()
            quit_events = [e for e in events if e.type == pygame.QUIT]
            if quit_events:
                player_action = ExitAction()

            key_events = [e for e in events if e.type == pygame.KEYDOWN]
            mouse_events = [e for e in events if e.type == pygame.MOUSEBUTTONDOWN]

            key_action = handle_keys(key_events, game_data.state)
            mouse_action = handle_mouse(mouse_events, game_data.constants, gfx_data.camera)

            if mouse_action:
                gui_action = gfx_data.windows.handle_click(game_data, gfx_data, mouse_action)
                if gui_action:
                    key_action = gui_action

            if key_action:
                handled, gui_action = gfx_data.windows.handle_key(game_data, gfx_data, key_action)
                if handled:
                    key_action = gui_action

            fullscreen = key_action.get(Event.fullscreen)
            move = key_action.get(Event.move)
            do_exit = key_action.get(Event.exit)
            left_click = mouse_action.get(Event.left_click)
            right_click = mouse_action.get(Event.right_click)
            level_up = key_action.get(Event.level_up)
            start_throwing_vial = key_action.get(Event.start_throwing_vial)
            show_help = key_action.get(Event.show_help)
            interact = key_action.get(Event.interact)

            if interact:
                for e in game_data.map.entities:
                    if e.pos.x == self.pos.x and e.pos.y == self.pos.y:
                        if e.stairs:
                            player_action = DescendStairsAction(self)
                            self.last_num_explored = None
                            game_data.story.next_story()
                            # TODO clear cooldowns?
                            break
                        elif e.name.startswith("Remains of"): # monster
                            if e.orig_name == "Arina":
                                game_data.prev_state.append(game_data.state)
                                game_data.state = GameStates.VICTORY
                                game_data.story.next_story()
                                gfx_data.windows.activate_wnd_for_state(game_data.state)
                            else:
                                player_action = LootAction(self)
                                e.name = "Looted r" + e.name[1:]
                                game_data.stats.loot_monster(e)
                            break
                else:
                    if config.conf.cooldown_mode != "always":
                        player_action = WaitAction(self)

            if show_help:
                game_data.prev_state.append(game_data.state)
                if game_data.state == GameStates.FORMULA_SCREEN:
                    game_data.state = GameStates.FORMULA_HELP_SCEEN
                elif game_data.state == GameStates.STORY_SCREEN:
                    game_data.state = GameStates.STORY_HELP_SCREEN
                else:
                    game_data.state = GameStates.GENERAL_HELP_SCREEN
                gfx_data.windows.activate_wnd_for_state(game_data.state)

            elif move:
                dx, dy = move
                destx = self.pos.x + dx
                desty = self.pos.y + dy

                if not game_data.map.is_blocked(destx, desty):
                    target = get_blocking_entites_at_location(game_data.map.entities, destx, desty)
                    if target and target.fighter:
                        player_action = AttackAction(self, target=target)
                    else:
                        player_action = MoveToPositionAction(self, targetpos=Pos(destx, desty))
                        gfx_data.camera.center_on(destx, desty)
                        game_data.stats.move_player(Pos(destx, desty))

            if game_data.state == GameStates.LEVEL_UP:
                gfx_data.windows.get(LevelUpWindow).visible = True

            if game_data.state == GameStates.TARGETING:
                if left_click:
                    targetx, targety = left_click.cx, left_click.cy
                    from util import Vec
                    distance = (self.pos - Vec(targetx, targety)).length()
                    if distance > game_data.targeting_formula.distance:
                        turn_results.append({"target_out_of_range": True, "targeting_formula": game_data.targeting_formula})
                    else:
                        player_action = ThrowVialAction(self, game_data.targeting_formula,
                                                        targetpos=(Pos(targetx, targety)))
                        # gfx_data.visuals.add_temporary(self.pos, Pos(targetx, targety), lifespan=distance * 0.1,
                        gfx_data.visuals.add_temporary(self.pos, Pos(targetx, targety), lifespan=0.2,
                                                       asset=gfx_data.assets.throwing_bottle)
                        game_data.state = game_data.prev_state.pop()
                elif right_click:
                    turn_results.append({"targeting_cancelled": True})

            if start_throwing_vial is not None:
                if start_throwing_vial >= len(self.caster.formulas):
                    game_data.log.add_message(Message("You don't have that formula yet", tcod.yellow))
                else:
                    formula = self.caster.formulas[start_throwing_vial]
                    if formula.targeted:
                        start_throwing_vial_results = {
                            "targeting_formula": formula,
                            "formula_idx": start_throwing_vial
                        }
                        turn_results.append(start_throwing_vial_results)
                    else:
                        player_action = ThrowVialAction(self, formula, targetpos=game_data.player.pos)

            if do_exit:
                if game_data.state == GameStates.TARGETING:
                    turn_results.append({"targeting_cancelled": True})
                else:
                    keep_playing = key_action.get(Event.keep_playing)
                    player_action = ExitAction(keep_playing)

            if fullscreen:
                display = (game_data.constants.window_size.width, game_data.constants.window_size.height)
                if pygame.display.get_driver() == 'x11':
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

            key_action = mouse_action = None  # clear them for next round

            for res in turn_results:
                game_data.targeting_formula = res.get("targeting_formula")
                if game_data.targeting_formula:
                    formula_idx = res.get("formula_idx")
                    if self.caster.is_on_cooldown(formula_idx):
                        game_data.log.add_message(self.caster.cooldown_message)
                    else:
                        game_data.prev_state.append(GameStates.PLAY)
                        game_data.state = GameStates.TARGETING

                        game_data.log.add_message(game_data.targeting_formula.targeting_message)

                targeting_cancelled = res.get("targeting_cancelled")
                if targeting_cancelled:
                    game_data.state = game_data.prev_state.pop()
                    game_data.log.add_message(Message("Targeting cancelled"))

                target_out_of_range = res.get("target_out_of_range")
                if target_out_of_range:
                    game_data.log.add_message(Message("Target out of range"))

            gfx_data.visuals.update(game_data, gfx_data)
            gfx_data.clock.tick(gfx_data.fps_per_second)
            pygame.display.flip()

        # end of no action
        assert player_action
        if type(player_action) == MoveToPositionAction:
            game_data.fov_recompute = True
        return player_action.execute(game_data, gfx_data)
