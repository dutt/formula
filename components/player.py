import pygame
import tcod
from attrdict import AttrDict

from components.action import MoveToPositionAction, AttackAction, ExitAction, ThrowVialAction, WaitAction, \
    DescendStairsAction
from components.caster import Caster
from components.drawable import Drawable
from components.fighter import Fighter
from components.level import Level
from entity import Entity, get_blocking_entites_at_location
from formula_builder import FormulaBuilder
from fov import recompute_fov
from game_states import GameStates
from graphics.pygame_gfx import render_all
from graphics.render_order import RenderOrder
from input_handlers import Event, handle_keys, handle_mouse
from messages import Message
from util import Pos


class Player(Entity):
    def __init__(self, assets):
        caster_component = Caster(num_slots=3, num_formulas=3)
        fighter_component = Fighter(hp=10, defense=0, power=3)
        level_component = Level()
        drawable_component = Drawable(assets.player)
        super(Player, self).__init__(0, 0, "Player", speed=100, blocks=True,
                                     render_order=RenderOrder.ACTOR,
                                     fighter=fighter_component, level=level_component, caster=caster_component,
                                     drawable=drawable_component)
        self.formula_builder = FormulaBuilder(self.caster.num_slots, self.caster.num_formulas)

    def take_turn(self, game_data, gfx_data):

        if self.action_points < 100:
            return None

        player_action = None
        targeting_formula = None
        self.caster.tick_cooldowns()

        menu_data = AttrDict({
            "currchoice": 0
        })

        while not player_action:

            turn_results = []

            if game_data.fov_recompute:
                recompute_fov(game_data.fov_map, game_data.player.pos.x, game_data.player.pos.y,
                              game_data.constants.fov_radius, game_data.constants.fov_light_walls,
                              game_data.constants.fov_algorithm)
            render_all(gfx_data, game_data, targeting_formula, self.formula_builder, menu_data)

            events = pygame.event.get()
            quit_events = [e for e in events if e.type == pygame.QUIT]
            if quit_events:
                player_action = ExitAction()

            key_events = [e for e in events if e.type == pygame.KEYDOWN]
            mouse_events = [e for e in events if e.type == pygame.MOUSEBUTTONDOWN]

            action = handle_keys(key_events, game_data.state)
            mouse_action = handle_mouse(mouse_events, game_data.constants, gfx_data.camera)

            fullscreen = action.get(Event.fullscreen)
            move = action.get(Event.move)
            do_exit = action.get(Event.exit)
            left_click = mouse_action.get(Event.left_click)
            right_click = mouse_action.get(Event.right_click)

            if mouse_action:
                gui_result = gfx_data.windows.handle_click(game_data, gfx_data, mouse_action)
                if gui_result:
                    action = gui_result

            level_up = action.get(Event.level_up)
            show_character_screen = action.get(Event.character_screen)
            show_formula_screen = action.get(Event.formula_screen)
            start_throwing_vial = action.get(Event.start_throwing_vial)
            show_help = action.get(Event.show_help)
            interact = action.get(Event.interact)

            if interact:
                for e in game_data.entities:
                    if e.stairs and e.pos.x == self.pos.x and e.pos.y == self.pos.y:
                        player_action = DescendStairsAction(self)
                        game_data.story.next_story()
                        # TODO clear cooldowns?
                        break
                else:
                    player_action = WaitAction(self)

            if show_help:
                game_data.prev_state.append(game_data.state)
                if game_data.state == GameStates.FORMULA_SCREEN:
                    game_data.state = GameStates.FORMULA_HELP_SCEEN
                elif game_data.state == GameStates.STORY_SCREEN:
                    game_data.state = GameStates.STORY_HELP_SCREEN
                else:
                    game_data.state = GameStates.GENERAL_HELP_SCREEN

            elif move:
                dx, dy = move
                destx = self.pos.x + dx
                desty = self.pos.y + dy

                if not game_data.map.is_blocked(destx, desty):
                    target = get_blocking_entites_at_location(game_data.entities, destx, desty)
                    if target and target.fighter:
                        player_action = AttackAction(self, target=target)
                    else:
                        player_action = MoveToPositionAction(self, targetpos=Pos(destx, desty))
                        gfx_data.camera.center_on(destx, desty)

            from map_objects.rect import Rect
            if left_click and game_data.state == GameStates.PLAY:  # UI clicked, not targeting
                right_panel_rect = Rect(0, 0, game_data.constants.right_panel_size.width,
                                        game_data.constants.right_panel_size.height)
                cx, cy = left_click.x, left_click.y
                if right_panel_rect.contains(cx, cy):  # right panel, cast formula?
                    casting_formula = None
                    formula_idx = None
                    for i in range(self.caster.num_formulas):
                        if Rect(10, 20 + i * 40, 10, 1).contains(cx, cy):
                            casting_formula = self.caster.formulas[i]
                            formula_idx = i
                            break
                    if casting_formula:
                        start_throwing_vial_results = {"targeting_formula": casting_formula, "formula_idx": formula_idx}
                        turn_results.append(start_throwing_vial_results)

            if show_character_screen:
                game_data.prev_state.append(game_data.state)
                game_data.state = GameStates.CHARACTER_SCREEN

            if game_data.state == GameStates.LEVEL_UP:
                choice = action.get("choice")
                if choice:
                    menu_data.currchoice += choice

            if game_data.state == GameStates.TARGETING:
                if left_click:
                    targetx, targety = left_click.cx, left_click.cy
                    # distance = (self.pos - Vec(targetx, targety)).length()
                    player_action = ThrowVialAction(self, targeting_formula, targetpos=(Pos(targetx, targety)))
                    # gfx_data.visuals.add_temporary(self.pos, Pos(targetx, targety), lifespan=distance * 0.1,
                    gfx_data.visuals.add_temporary(self.pos, Pos(targetx, targety), lifespan=0.2,
                                                   asset=gfx_data.assets.throwing_bottle)
                    game_data.state = game_data.prev_state.pop()
                elif right_click:
                    turn_results.append({"targeting_cancelled": True})

            if game_data.state == GameStates.STORY_SCREEN:
                next = action.get("next")
                if next:
                    if game_data.story.is_last_page:
                        game_data.state = game_data.prev_state.pop()
                    else:
                        game_data.story.next_page()

            if level_up:
                if menu_data.currchoice == 0:
                    self.formula_builder.add_slot()
                elif menu_data.currchoice == 1:
                    self.formula_builder.add_formula()
                game_data.state = game_data.prev_state.pop()

            if start_throwing_vial is not None:
                if start_throwing_vial >= len(self.caster.formulas):
                    game_data.log.add_message(Message("You don't have that formula yet", tcod.yellow))
                else:
                    start_throwing_vial_results = {"targeting_formula": self.caster.formulas[start_throwing_vial],
                                                   "formula_idx": start_throwing_vial}
                    turn_results.append(start_throwing_vial_results)

            if show_formula_screen:
                game_data.prev_state.append(game_data.state)
                game_data.state = GameStates.FORMULA_SCREEN

            if game_data.state == GameStates.FORMULA_SCREEN:
                slot = action.get("slot")
                if slot is not None:
                    self.formula_builder.currslot = slot

                ingredient = action.get("ingredient")
                if ingredient:
                    self.formula_builder.set_slot(self.formula_builder.currslot, ingredient)
                    # go to next slot
                    next_num = (self.formula_builder.currslot + 1) % self.formula_builder.num_slots
                    self.formula_builder.currslot = next_num

                next_formula = action.get("next_formula")
                if next_formula:
                    next_num = (self.formula_builder.currformula + next_formula) % self.formula_builder.num_formula
                    self.formula_builder.currformula = next_num
                    # go to first slot
                    self.formula_builder.currslot = 0

                next_slot = action.get("next_slot")
                if next_slot:
                    next_num = (self.formula_builder.currslot + next_slot) % self.formula_builder.num_slots
                    self.formula_builder.currslot = next_num

            if do_exit:
                if game_data.state == GameStates.FORMULA_SCREEN:
                    self.caster.set_formulas(self.formula_builder.evaluate())
                    gfx_data.camera.center_on(self.pos.x, self.pos.y)
                    game_data.state = game_data.prev_state.pop()
                elif game_data.state in [GameStates.CHARACTER_SCREEN,
                                         GameStates.FORMULA_HELP_SCEEN,
                                         GameStates.GENERAL_HELP_SCREEN,
                                         GameStates.WELCOME_SCREEN,
                                         GameStates.STORY_SCREEN,
                                         GameStates.STORY_HELP_SCREEN]:
                    game_data.state = game_data.prev_state.pop()
                elif game_data.state == GameStates.TARGETING:
                    turn_results.append({"targeting_cancelled": True})
                else:
                    player_action = ExitAction()

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

            action = mouse_action = None  # clear them for next round

            for res in turn_results:
                targeting_formula = res.get("targeting_formula")
                if targeting_formula:
                    formula_idx = res.get("formula_idx")
                    if self.caster.is_on_cooldown(formula_idx):
                        game_data.log.add_message(self.caster.cooldown_message)
                    else:
                        game_data.prev_state.append(GameStates.PLAY)
                        game_data.state = GameStates.TARGETING

                        game_data.log.add_message(targeting_formula.targeting_message)

                targeting_cancelled = res.get("targeting_cancelled")
                if targeting_cancelled:
                    game_data.state = game_data.prev_state.pop()
                    game_data.log.add_message(Message("Targeting cancelled"))

            gfx_data.visuals.update()
            gfx_data.clock.tick(gfx_data.fps_per_second)

        # end of no action
        assert player_action
        if type(player_action) == MoveToPositionAction:
            game_data.fov_recompute = True
        return player_action.execute(game_data)
