from enum import Enum, auto
import math

import tcod
from attrdict import AttrDict as attribdict

from game_states import GameState
from menu import inventory_menu, level_up_menu, character_screen, spellmaker_menu, help_screen, welcome_screen
from util import Size


class RenderOrder(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)
    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and tcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ", ".join(names)

    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

        tcod.console_set_default_foreground(panel, tcod.white)
        if name.strip() != "":
            text = "{}: {}/{}".format(name, value, maximum)
        else:
            text = "{}/{}".format(value, maximum)
        tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER, text)


def get_line(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


def render_all(con, bottom_panel, right_panel,
               entities, player,
               game_map, fov_map, fov_recompute, log,
               screen_size, bar_width, bottom_panel_height, bottom_panel_y,
               mouse, colors, state, targeting_spell, spellbuilder):
    def draw_ground():
        for y in range(game_map.height):
            for x in range(game_map.width):
                wall = game_map.tiles[x][y].block_sight
                visible = tcod.map_is_in_fov(fov_map, x, y)
                # visible = True
                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get("light_wall"))
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get("light_ground"))
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get("dark_wall"))
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get("dark_ground"))

    def mouse_pos():
        return attribdict({"cx": mouse.cx - right_panel.width, "cy": mouse.cy})

    def draw_entities_and_action():
        targeting_coords = []
        if state == GameState.TARGETING:
            points = get_line((player.x, player.y), (mouse.cx, mouse.cy))
            hit_wall = False
            for idx, p in enumerate(points):
                px, py = p
                if idx > targeting_spell.distance or hit_wall:
                    tcod.console_set_char_foreground(con, px, py, tcod.grey)
                elif game_map.tiles[px][py].block_sight:
                    hit_wall = True
                    tcod.console_set_char_foreground(con, px, py, tcod.grey)
                else:
                    tcod.console_set_char_foreground(con, px, py, tcod.red)
                tcod.console_set_char(con, px, py, '.')
            if player.distance(mouse.cx, mouse.cy) < targeting_spell.distance:
                tcod.console_set_char(con, mouse.cx, mouse.cy, 'X')
                if targeting_spell.area > 1:  # aoe, let's draw the area
                    for x in range(math.ceil(mouse.cx - targeting_spell.distance),
                                   math.ceil(mouse.cx + targeting_spell.distance)):
                        for y in range(math.ceil(mouse.cy - targeting_spell.distance),
                                       math.ceil(mouse.cy + targeting_spell.distance)):
                            dist = (math.sqrt((x - mouse.cx) ** 2 + (y - mouse.cy) ** 2))
                            if dist < targeting_spell.area:
                                tcod.console_set_char_foreground(con, x, y, tcod.red)
                                tcod.console_set_char(con, x, y, 'x')
                                targeting_coords.append((x, y))
                else:
                    targeting_coords = [(mouse.cx, mouse.cy)]

        ordered_entities = sorted(entities, key=lambda e: e.render_order.value)
        for entity in ordered_entities:
            render_entity(con, entity, fov_map, game_map)
            if (entity.x, entity.y) in targeting_coords and \
                    player.distance(entity.x, entity.y) < targeting_spell.distance and \
                    tcod.map_is_in_fov(fov_map, entity.x, entity.y):
                tcod.console_set_char_background(con, entity.x, entity.y, tcod.red)

    mouse = mouse_pos()

    tcod.console_clear(con)

    if fov_recompute:
        draw_ground()

    draw_entities_and_action()

    tcod.console_blit(con, 0, 0, screen_size.width - right_panel.width, screen_size.height, 0, right_panel.width, 0)

    # right panel
    tcod.console_set_default_background(right_panel, tcod.black)
    tcod.console_clear(right_panel)

    y = 2
    x = 1
    tcod.console_rect(right_panel, 0, 0, 10, 10, clr=False, flag=tcod.BKGND_NONE)

    tcod.console_print_ex(right_panel, x, 1, tcod.BKGND_NONE, tcod.LEFT,
                          "Spells:")
    for idx, spell in enumerate(player.caster.spells):
        if player.caster.is_on_cooldown(idx):
            render_bar(right_panel, 1, y, right_panel.width, "", player.caster.get_cooldown(idx),
                       spell.cooldown, tcod.dark_azure, tcod.black)
        else:
            tcod.console_print_ex(right_panel, x, y, tcod.BKGND_NONE, tcod.LEFT,
                                  "{}: {}".format(idx + 1, spell.text_repr))
        y += 2

    tcod.console_blit(right_panel, 0, 0, screen_size.width, screen_size.height, 0, 0, 0)

    # bottom panel
    tcod.console_set_default_background(bottom_panel, tcod.black)
    tcod.console_clear(bottom_panel)

    y = 1
    for msg in log.messages:
        tcod.console_set_default_foreground(bottom_panel, msg.color)
        tcod.console_print_ex(bottom_panel, log.x, y, tcod.BKGND_NONE, tcod.LEFT, msg.text)
        y += 1

    render_bar(bottom_panel, 1, 1, bar_width, "HP", player.fighter.hp, player.fighter.max_hp,
               tcod.light_red, tcod.darker_red)
    tcod.console_print_ex(bottom_panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT,
                          "Station level {}".format(game_map.dungeon_level))

    tcod.console_set_default_foreground(bottom_panel, tcod.light_grey)
    tcod.console_print_ex(bottom_panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT,
                          get_names_under_mouse(mouse, entities, fov_map))

    tcod.console_blit(bottom_panel, 0, 0, screen_size.width, bottom_panel_height, 0, 0, bottom_panel_y)

    # optionally draw menus on top
    if state in [GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY]:
        if state == GameState.SHOW_INVENTORY:
            title = "Press the key next to the item to use it, or Esc to cancel"
        else:
            title = "Press the key next to the item to drop it, or Esc to cancel"
        inventory_menu(con, title + "\n", player, 50, screen_size)
    elif state == GameState.LEVEL_UP:
        level_up_menu(con, "Level up, please choose:", player, 40, screen_size)
    elif state == GameState.CHARACTER_SCREEN:
        character_screen(player, Size(30, 10), screen_size)
    elif state == GameState.SPELLMAKER_SCREEN:
        spellmaker_menu(spellbuilder, Size(30, 10), screen_size)
    elif state == GameState.SHOW_HELP:
        help_screen(screen_size)
    elif state == GameState.WELCOME_SCREEN:
        welcome_screen(screen_size)


def render_entity(con, entity, fov_map, game_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or \
            (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def clear_entity(con, entity):
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)
