import tcod

import gfx
from input_handlers import Event, handle_keys, handle_mouse
from game_states import GameState
from fov import initialize_fov, recompute_fov
from entity import get_blocking_entites_at_location
from death import kill_player, kill_monster
from messages import Message
from loader_functions.init_new_game import get_constants, get_game_variables
from spell_engine import SpellBuilder
from spell_engine import SpellEngine

def play_game(player, entities, gmap, log, state, con, bottom_panel, right_panel, constants):
    key = tcod.Key()
    mouse = tcod.Mouse()

    fov_recompute = True
    fov_map = initialize_fov(gmap)

    prev_state = GameState.PLAYER_TURN

    targeting_spell=None
    targeting_item=None
    spellbuilder = SpellBuilder(player.caster.num_slots, player.caster.num_spells)

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          constants.fov_radius, constants.fov_light_walls, constants.fov_algorithm)

        gfx.render_all(con, bottom_panel, right_panel, entities, player,
                       gmap, fov_map, fov_recompute, log,
                       constants.screen_size, constants.bar_width, constants.panel_height, constants.panel_y,
                       mouse, constants.colors, state, targeting_spell, spellbuilder)
        tcod.console_flush()
        gfx.clear_all(con, entities)

        action = handle_keys(key, state)
        mouse_action = handle_mouse(mouse)

        player_turn_results = []

        move = action.get(Event.move)
        exit = action.get(Event.exit)
        pickup = action.get(Event.pickup)
        show_inventory = action.get(Event.show_inventory)
        drop_inventory = action.get(Event.drop_inventory)
        inventory_index = action.get(Event.inventory_index)
        left_click = mouse_action.get(Event.left_click)
        right_click = mouse_action.get(Event.right_click)
        take_stairs = action.get(Event.take_stairs)
        level_up = action.get(Event.level_up)
        show_character_screen = action.get(Event.character_screen)
        wait = action.get(Event.wait)
        show_spellmaker_screen = action.get(Event.spellmaker_screen)
        start_casting_spell = action.get(Event.start_casting_spell)
        show_help = action.get(Event.show_help)

        if wait:
            state = GameState.ENEMY_TURN

        elif show_help:
            prev_state = state
            state = GameState.SHOW_HELP

        elif move and state == GameState.PLAYER_TURN:
            dx, dy = move
            destx = player.x + dx
            desty = player.y + dy
            if not gmap.is_blocked(destx, desty):
                target = get_blocking_entites_at_location(entities, destx, desty)
                if target:
                    player_turn_results.extend(player.fighter.attack(target))
                else:
                    player.move(dx, dy)
                    fov_recompute = True
            state = GameState.ENEMY_TURN

        elif pickup and state == GameState.PLAYER_TURN:
            for e in entities:
                if e.item and e.x == player.x and e.y == player.y:
                    results = player.inventory.add_item(e)
                    player_turn_results.extend(results)
                    break
            else:
                log.add_message(Message("Nothing here", tcod.yellow))

        if state == GameState.ENEMY_TURN:
            for e in entities:
                if e.ai:
                    enemy_results = e.ai.take_turn(player, fov_map, gmap, entities)
                    for res in enemy_results:
                        msg = res.get("message")
                        if msg:
                            log.add_message(msg)

                        dead_entity = res.get("dead")
                        if dead_entity:
                            if dead_entity == player:
                                msg, state = kill_player(dead_entity)
                            else:
                                msg = kill_monster(dead_entity)
                            log.add_message(msg)

                            if state == GameState.PLAYER_DEAD:
                                break
                if state == GameState.PLAYER_DEAD:
                    break
            else:
                state = GameState.PLAYER_TURN

        if show_inventory:
            prev_state = state
            state = GameState.SHOW_INVENTORY

        if drop_inventory:
            prev_state = state
            state = GameState.DROP_INVENTORY

        if show_character_screen:
            prev_state = state
            state = GameState.CHARACTER_SCREEN

        if inventory_index is not None and prev_state != GameState.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]

            if state == GameState.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif state == GameState.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop(item))

        if state == GameState.TARGETING:
            if left_click:
                target_x, target_y = left_click
                if targeting_spell:
                    spell_cast_results = targeting_spell.apply(entities=entities, fov_map=fov_map, caster=player,
                                                               target_x=target_x, target_y=target_y)
                    player_turn_results.extend(spell_cast_results)
                elif targeting_item:
                    item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                            target_x=target_x, target_y=target_y)
                    player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({"targeting_cancelled" : True})

        if take_stairs and state == GameState.PLAYER_TURN:
            for e in entities:
                if e.stairs and e.x == player.x and e.y == player.y:
                    entities = gmap.next_floor(player, log, constants)
                    fov_map = initialize_fov(gmap)
                    fov_recompute = True
                    tcod.console_clear(con)
                    break
            else:
                log.add_message(Message("There are no stairs here", tcod.yellow))

        if level_up:
            if level_up == "hp":
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == "str":
                player.fighter.base_power += 1
            elif level_up == "def":
                player.fighter.base_defense += 1
            state = prev_state

        if start_casting_spell is not None:
            if start_casting_spell >= len(player.caster.spells):
                log.add_message(Message("You don't have that spell yet", tcod.yellow))
            else:
                start_cast_spell_results = {"targeting_spell": player.caster.spells[start_casting_spell]}
                player_turn_results.append(start_cast_spell_results)

        if show_spellmaker_screen:
            prev_state = state
            state = GameState.SPELLMAKER_SCREEN

        if state == GameState.SPELLMAKER_SCREEN:
            slot = action.get("slot")
            if slot is not None:
                print("current slot will be {}".format(slot))
                spellbuilder.currslot = slot

            ingredient = action.get("ingredient")
            if ingredient:
                print("setting slot {} to {}".format(spellbuilder.currslot, ingredient))
                spellbuilder.set_slot(spellbuilder.currslot, ingredient)

            next_spell = action.get("next_spell")
            if next_spell:
                spellbuilder.currspell = (spellbuilder.currspell+1) % spellbuilder.num_spells

        if exit:
            if state == GameState.SPELLMAKER_SCREEN:
                player.caster.spells = SpellEngine.evaluate(spellbuilder)
                state = prev_state
            elif state in [GameState.SHOW_INVENTORY,
                         GameState.DROP_INVENTORY,
                         GameState.CHARACTER_SCREEN,
                         GameState.SPELLMAKER_SCREEN,
                         GameState.SHOW_HELP]:
                state = prev_state
            elif state == GameState.TARGETING:
                player_turn_results.append({"targeting_cancelled" : True})
            else:
                return True

        for res in player_turn_results:
            msg = res.get("message")
            if msg:
                log.add_message(msg)

            dead_entity = res.get("dead")
            if dead_entity:
                if dead_entity == player:
                    msg, state = kill_player(dead_entity)
                else:
                    msg = kill_monster(dead_entity)
                log.add_message(msg)

            item_added = res.get("item_added")
            if item_added:
                entities.remove(item_added)
                state = GameState.ENEMY_TURN

            item_consumed = res.get("consumed")
            if item_consumed:
                prev_state = state
                state = GameState.ENEMY_TURN

            item_dropped = res.get("item_dropped")
            if item_dropped:
                entities.append(item_dropped)
                state = GameState.ENEMY_TURN

            targeting = res.get("targeting")
            if targeting:
                prev_state = GameState.PLAYER_TURN
                state = GameState.TARGETING

                targeting_item = targeting
                log.add_message(targeting_item.item.targeting_message)

            targeting_spell = res.get("targeting_spell")
            if targeting_spell:
                prev_state = GameState.PLAYER_TURN
                state = GameState.TARGETING

                log.add_message(targeting_spell.targeting_message)

            targeting_cancelled = res.get("targeting_cancelled")
            if targeting_cancelled:
                state = prev_state
                log.add_message(Message("Targeting cancelled"))

            xp = res.get("xp")
            if xp:
                leveled_up = player.level.add_xp(xp)
                log.add_message(Message("You gain {} xp".format(xp)))
                if leveled_up:
                    log.add_message(Message("You grow stronger, reached level {}".format(player.level.current_level), tcod.yellow))
                    prev_state = state
                    state = GameState.LEVEL_UP

            equip = res.get("equip")
            if equip:
                equip_results = player.equipment.toggle_equip(equip)
                for equip_result in equip_results:
                    equipped = equip_result.get("equipped")
                    dequipped = equip_result.get("dequipped")
                    if equipped:
                        log.add_message(Message("You equipped the {}".format(equipped.name)))

                    if dequipped:
                        log.add_message(Message("You dequipped the {}".format(dequipped.name)))
                state = GameState.ENEMY_TURN

            cast = res.get("cast")
            if cast is not None:
                #spell = res.get("spell")
                state = GameState.ENEMY_TURN

        #fullscreen = action.get(event.fullscreen)
        #if fullscreen:
            #exiting fullscreen doesn't restore resolution
            #tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

def main():
    constants = get_constants()
    player, entities, gmap, log, state = get_game_variables(constants)
    prev_state = state

    tcod.console_set_custom_font("/home/mikael/workspace/libtcod/data/fonts/arial10x10.png", tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(constants.screen_size.width, constants.screen_size.height, "spellmaker", False)

    con = tcod.console_new(constants.screen_size.width, constants.screen_size.height)
    bottom_panel = tcod.console_new(constants.screen_size.width, constants.bottom_panel_height)
    right_panel = tcod.console_new(constants.right_panel_size.width, constants.right_panel_size.height)

    play_game(player, entities, gmap, log, state, con, bottom_panel, right_panel, constants)

if __name__ == '__main__':
    try:
        main()
    except:
        import traceback
        traceback.print_exc()
