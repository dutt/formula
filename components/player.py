import time

import tcod

import gfx
from components.action import MoveAction, AttackAction, ExitAction, CastSpellAction
from components.caster import Caster
from components.fighter import Fighter
from components.level import Level
from entity import Entity, get_blocking_entites_at_location, Pos
from fov import recompute_fov, initialize_fov
from game_states import GameStates
from gfx import RenderOrder
from input_handlers import Event, handle_keys, handle_mouse
from messages import Message
from spell_engine import SpellBuilder, SpellEngine

key = tcod.Key()
mouse = tcod.Mouse()


class Player(Entity):
    def __init__(self):
        caster_component = Caster(num_slots=3, num_spells=3)
        fighter_component = Fighter(hp=100, defense=1, power=3)
        level_component = Level()
        super(Player, self).__init__(0, 0, '@', tcod.white, "Player", speed=100, blocks=True,
                                     render_order=RenderOrder.ACTOR,
                                     fighter=fighter_component, level=level_component, caster=caster_component)

        self.con = self.bottom_panel = self.right_panel = None

    def set_gui(self, con, bottom_panel, right_panel):
        self.con = con
        self.bottom_panel = bottom_panel
        self.right_panel = right_panel

    def set_initial_state(self, state, game_data):
        game_data.state = state
        game_data.prev_state = []

    def take_turn(self, game_data):
        assert self.con
        assert self.bottom_panel
        assert self.right_panel

        if self.action_points <= 0:
            return None

        player_action = None

        targeting_spell = None
        self.caster.tick_cooldowns()
        spellbuilder = SpellBuilder(self.caster.num_slots, self.caster.num_spells)

        while not player_action:

            turn_results = []

            if game_data.fov_recompute:
                recompute_fov(game_data.fov_map, game_data.player.pos.x, game_data.player.pos.y,
                              game_data.constants.fov_radius, game_data.constants.fov_light_walls,
                              game_data.constants.fov_algorithm)
            gfx.render_all(self.con, self.bottom_panel, self.right_panel,
                           game_data.entities, self,
                           game_data.map, game_data.fov_map, game_data.fov_recompute, game_data.log,
                           game_data.constants, mouse, game_data.state, targeting_spell, spellbuilder)

            tcod.console_flush()

            gfx.clear_all(self.con, game_data.entities)

            tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
            action = handle_keys(key, game_data.state)
            mouse_action = handle_mouse(mouse)
            if not action and not mouse_action:
                time.sleep(0.01)  # avoid busy looping
                continue

            fullscreen = action.get(Event.fullscreen)
            move = action.get(Event.move)
            do_exit = action.get(Event.exit)
            left_click = mouse_action.get(Event.left_click)
            left_map_click = (left_click[0] - self.right_panel.width, left_click[1]) if left_click else None
            right_click = mouse_action.get(Event.right_click)
            level_up = action.get(Event.level_up)
            show_character_screen = action.get(Event.character_screen)
            show_spellmaker_screen = action.get(Event.spellmaker_screen)
            start_casting_spell = action.get(Event.start_casting_spell)
            show_help = action.get(Event.show_help)
            interact = action.get(Event.interact)

            if interact:
                for e in game_data.entities:
                    if e.stairs and e.pos.x == self.pos.x and e.pos.y == self.pos.y:
                        game_data.entities = game_data.map.next_floor(game_data.player, game_data.log,
                                                                      game_data.constants,
                                                                      game_data.entities, game_data.timesystem)
                        game_data.prev_state = [GameStates.PLAY]
                        game_data.state = GameStates.SPELLMAKER_SCREEN
                        game_data.fov_map = initialize_fov(game_data.map)
                        game_data.fov_recompute = True
                        tcod.console_clear(self.con)
                        break
                else:
                    print("waiting")
                if game_data.state == GameStates.SPELLMAKER_SCREEN:
                    # we descended
                    continue

            if show_help:
                game_data.prev_state.append(game_data.state)
                if game_data.state == GameStates.SPELLMAKER_SCREEN:
                    game_data.state = GameStates.SPELLMAKER_HELP_SCEEN
                else:
                    game_data.state = GameStates.GENERAL_HELP_SCREEN

            elif move:
                dx, dy = move
                destx = self.pos.x + dx
                desty = self.pos.y + dy
                if not game_data.map.is_blocked(destx, desty):
                    target = get_blocking_entites_at_location(game_data.entities, destx, desty)
                    if target:
                        player_action = AttackAction(self, target=target)
                    else:
                        player_action = MoveAction(self, targetpos=Pos(destx, desty))

            from map_objects.rect import Rect
            right_panel_rect = Rect(0, 0, self.right_panel.width, self.right_panel.height)
            if left_click and game_data.state == GameStates.PLAY:  # UI clicked, not targeting
                cx, cy = left_click
                if right_panel_rect.contains(cx, cy):  # right panel, cast spell?
                    casting_spell = None
                    spell_idx = None
                    for i in range(self.caster.num_spells):
                        if Rect(1, 2 + i * 2, 10, 1).contains(cx, cy):
                            casting_spell = self.caster.spells[i]
                            spell_idx = i
                            break
                    if casting_spell:
                        start_cast_spell_results = {"targeting_spell": casting_spell, "spell_idx": spell_idx}
                        turn_results.append(start_cast_spell_results)

            if show_character_screen:
                game_data.prev_state.append(game_data.state)
                game_data.state = GameStates.CHARACTER_SCREEN

            if game_data.state == GameStates.TARGETING:
                if left_map_click:
                    targetx, targety = left_map_click
                    player_action = CastSpellAction(self, targeting_spell, targetpos=(Pos(targetx, targety)))
                    game_data.state = game_data.prev_state.pop()
                elif right_click:
                    turn_results.append({"targeting_cancelled": True})

            if level_up:
                if level_up == "hp":
                    self.fighter.base_max_hp += 20
                    self.fighter.hp += 20
                elif level_up == "str":
                    self.fighter.base_power += 1
                elif level_up == "def":
                    self.fighter.base_defense += 1
                game_data.state = game_data.prev_state.pop()

            if start_casting_spell is not None:
                if start_casting_spell >= len(self.caster.spells):
                    game_data.log.add_message(Message("You don't have that spell yet", tcod.yellow))
                else:
                    start_cast_spell_results = {"targeting_spell": self.caster.spells[start_casting_spell],
                                                "spell_idx": start_casting_spell}
                    turn_results.append(start_cast_spell_results)

            if show_spellmaker_screen:
                game_data.prev_state.append(game_data.state)
                game_data.state = GameStates.SPELLMAKER_SCREEN

            if game_data.state == GameStates.SPELLMAKER_SCREEN:
                slot = action.get("slot")
                if slot is not None:
                    spellbuilder.currslot = slot

                ingredient = action.get("ingredient")
                if ingredient:
                    spellbuilder.set_slot(spellbuilder.currslot, ingredient)

                next_spell = action.get("next_spell")
                if next_spell:
                    spellbuilder.currspell = (spellbuilder.currspell + next_spell) % spellbuilder.num_spells

                next_slot = action.get("next_slot")
                if next_slot:
                    spellbuilder.currslot = (spellbuilder.currslot + next_slot) % spellbuilder.num_slots

            if do_exit:
                if game_data.state == GameStates.SPELLMAKER_SCREEN:
                    self.caster.set_spells(SpellEngine.evaluate(spellbuilder))
                    game_data.state = game_data.prev_state.pop()
                elif game_data.state in [GameStates.CHARACTER_SCREEN,
                                         GameStates.SPELLMAKER_HELP_SCEEN,
                                         GameStates.GENERAL_HELP_SCREEN]:
                    game_data.state = game_data.prev_state.pop()
                elif game_data.state == GameStates.TARGETING:
                    turn_results.append({"targeting_cancelled": True})
                elif game_data.state == GameStates.WELCOME_SCREEN:
                    game_data.state = GameStates.SPELLMAKER_SCREEN
                else:
                    player_action = ExitAction()

            action = mouse_action = None  # clear them for next round

            for res in turn_results:
                targeting_spell = res.get("targeting_spell")
                if targeting_spell:
                    spell_idx = res.get("spell_idx")
                    if self.caster.is_on_cooldown(spell_idx):
                        game_data.log.add_message(self.caster.cooldown_message)
                    else:
                        game_data.prev_state.append(GameStates.PLAY)
                        game_data.state = GameStates.TARGETING

                        game_data.log.add_message(targeting_spell.targeting_message)

                targeting_cancelled = res.get("targeting_cancelled")
                if targeting_cancelled:
                    game_data.state = game_data.prev_state.pop()
                    game_data.log.add_message(Message("Targeting cancelled"))

                xp = res.get("xp")
                if xp:
                    leveled_up = self.level.add_xp(xp)
                    game_data.log.add_message(Message("You gain {} xp".format(xp)))
                    if leveled_up:
                        game_data.log.add_message(
                                Message("You grow stronger, reached level {}".format(self.level.current_level),
                                        tcod.yellow))
                        game_data.prev_state.append(game_data.state)
                        game_data.state = GameStates.LEVEL_UP

        # end of no action
        assert player_action
        if type(player_action) == MoveAction:
            game_data.fov_recompute = True
        return player_action.execute(game_data)
