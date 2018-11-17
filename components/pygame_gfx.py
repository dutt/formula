import math

import pygame
import tcod
from attrdict import AttrDict

import util
from game_states import GameStates
from graphics.assets import Assets
from graphics.constants import CELL_HEIGHT, CELL_WIDTH, colors
from spell_engine import SpellEngine
from util import Pos


def initialize(constants):
    pygame.display.init()
    pygame.display.set_caption("Formulas")
    pygame.font.init()
    main = pygame.display.set_mode((constants.window_size.width, constants.window_size.height))
    assets = Assets()
    return AttrDict({
        "main": main,
        "assets": assets
    })


def display_text(surface, text, font, coords, text_color=colors.WHITE, bg_color=None, center=False):
    if bg_color:
        text_surface = font.render(text, False, text_color, bg_color)
    else:
        text_surface = font.render(text, False, text_color)

    rect = text_surface.get_rect()
    if center:
        rect.center = coords
    else:
        rect.topleft = coords

    surface.blit(text_surface, rect)


def display_lines(surface, font, lines, x=50, starty=50):
    y = starty
    for line in lines:
        display_text(surface, line, font, (x, y))
        y += 20


def display_menu(gfx_data, lines, size):
    surface = pygame.Surface(size)
    display_lines(surface, gfx_data.assets.font_message, lines)
    gfx_data.main.blit(surface, (200, 200))


def render_bar(surface, assets, pos, width, current, maxval, color, bgcolor, height=30, text=None):
    current_length = max(0, (current / maxval) * width)
    pygame.draw.rect(surface, bgcolor, pygame.Rect(pos.x, pos.y, width, height))
    pygame.draw.rect(surface, color, pygame.Rect(pos.x, pos.y, current_length, height))
    msg = "{}/{}".format(current, maxval)
    display_text(surface, msg, assets.font_message, (pos.x + 10, pos.y + 5))


def render_all(gfx_data, game_data, targeting_spell, spellbuilder, menu_data):
    gfx_data.main.fill(game_data.constants.colors.dark_wall)
    assets = gfx_data.assets
    panel_width = game_data.constants.right_panel_size.width
    main = gfx_data.main

    def draw_terrain():
        for x in range(game_data.map.width):
            for y in range(game_data.map.height):
                wall = game_data.map.tiles[x][y].block_sight
                visible = tcod.map_is_in_fov(game_data.fov_map, x, y)
                # visible = True
                if visible:
                    if wall:
                        main.blit(assets.light_wall[0],
                                  (panel_width + x * CELL_WIDTH,
                                   y * CELL_HEIGHT))
                    else:
                        main.blit(assets.light_floor[0],
                                  (panel_width + x * CELL_WIDTH,
                                   y * CELL_HEIGHT))
                    game_data.map.tiles[x][y].explored = True
                elif game_data.map.tiles[x][y].explored:
                    if wall:
                        main.blit(assets.dark_wall[0],
                                  (panel_width + x * CELL_WIDTH,
                                   y * CELL_HEIGHT))
                    else:
                        main.blit(assets.dark_floor[0],
                                  (panel_width + x * CELL_WIDTH,
                                   y * CELL_HEIGHT))

    def draw_entities():
        rendering_sorted = sorted(game_data.entities, key=lambda e: e.render_order.value)
        for e in rendering_sorted:
            if e.drawable and tcod.map_is_in_fov(game_data.fov_map, e.pos.x, e.pos.y):
                main.blit(e.drawable.asset[0],
                          (panel_width + e.pos.x * CELL_WIDTH,
                           e.pos.y * CELL_HEIGHT))

    def draw_message_log():
        y = 800
        messages = game_data.log.messages
        for idx, msg in enumerate(messages[-7:]):
            display_text(main, msg.text, assets.font_message, (200, y + idx * 20), msg.color)

    def draw_bottom_panel():
        render_bar(main, assets, Pos(20, 940), 100, game_data.player.fighter.hp, game_data.player.fighter.max_hp,
                   (160, 0, 0), (100, 0, 0))
        draw_message_log()

    def draw_right_panel():
        display_text(main, "Formulas", assets.font_title, (10, 20))
        player = game_data.player
        y = 50
        for idx, spell in enumerate(player.caster.spells):
            if player.caster.is_on_cooldown(idx):
                render_bar(main, assets, Pos(20, y + idx * 20), 80, player.caster.get_cooldown(idx), spell.cooldown,
                           (0, 127, 255), colors.BLACK)

            else:
                msg = "{}: {}".format(idx + 1, spell.text_repr)
                display_text(main, msg, assets.font_message, (10, y + idx * 20))
            y += 40

    def global_pos_to_map_pos(x, y):
        return x - panel_width, y

    def map_pos_to_tile(x, y):
        return x // CELL_WIDTH, y // CELL_HEIGHT

    def get_tile_rect(x, y):
        return panel_width + x * CELL_WIDTH, y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT

    def draw_targeting():
        max_dist = targeting_spell.distance * CELL_WIDTH
        pos = pygame.mouse.get_pos()
        targeting_surface = pygame.Surface(game_data.constants.window_size.tuple())

        # find targeted tile
        map_pos = global_pos_to_map_pos(pos[0], pos[1])
        tile = map_pos_to_tile(map_pos[0], map_pos[1])
        rect = get_tile_rect(tile[0], tile[1])
        rect_center = rect[0] + CELL_WIDTH / 2, rect[1] + CELL_HEIGHT / 2

        # find player position
        orig = (panel_width + game_data.player.pos.x * CELL_WIDTH, game_data.player.pos.y * CELL_HEIGHT)
        orig = (orig[0] + CELL_WIDTH / 2, orig[1] + CELL_HEIGHT / 2)  # centered

        dist = util.distance(orig[0], orig[1], rect_center[0], rect_center[1])
        if dist > max_dist:
            vec = (pos[0] - orig[0], pos[1] - orig[1])
            length = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
            normalized = (vec[0] / length, vec[1] / length)
            partial_dist = (max_dist / dist) * dist
            red_part = (orig[0] + normalized[0] * partial_dist, orig[1] + normalized[1] * partial_dist)
            pygame.draw.line(targeting_surface, (255, 0, 0), orig, red_part)
            pygame.draw.line(targeting_surface, (100, 100, 100), red_part, rect_center)
            pygame.draw.rect(targeting_surface, (100, 100, 100), rect)
        elif targeting_spell.area == 1:  # no aoe
            pygame.draw.line(targeting_surface, (255, 0, 0), orig, rect_center)
            pygame.draw.rect(targeting_surface, (255, 0, 0), rect)
        else:
            pygame.draw.line(main, (255, 0, 0), orig, rect_center)

            for x in range(math.ceil(tile[0] - targeting_spell.distance),
                           math.ceil(tile[0] + targeting_spell.distance)):
                for y in range(math.ceil(tile[1] - targeting_spell.distance),
                               math.ceil(tile[1] + targeting_spell.distance)):
                    dist = (math.sqrt((x - tile[0]) ** 2 + (y - tile[1]) ** 2))
                    if dist < targeting_spell.area:
                        tile_rect = get_tile_rect(x, y)
                        pygame.draw.rect(targeting_surface, (255, 0, 0), tile_rect)
        targeting_surface.set_alpha(100)
        gfx_data.main.blit(targeting_surface, (0, 0))

    draw_terrain()
    draw_entities()
    draw_bottom_panel()
    draw_right_panel()
    if game_data.state == GameStates.TARGETING:
        draw_targeting()

    if game_data.state == GameStates.WELCOME_SCREEN:
        welcome_menu(gfx_data)
    elif game_data.state == GameStates.GENERAL_HELP_SCREEN:
        help_menu(gfx_data)
    elif game_data.state == GameStates.SPELLMAKER_SCREEN:
        spellmaker_menu(gfx_data, spellbuilder)
    elif game_data.state == GameStates.SPELLMAKER_HELP_SCEEN:
        spellmaker_help_menu(gfx_data)
    elif game_data.state == GameStates.LEVEL_UP:
        levelup_menu(gfx_data, spellbuilder, menu_data)

    pygame.display.flip()


def spellmaker_menu(gfx_data, spellbuilder):
    surface = pygame.Surface((800, 600))
    linediff = 10
    y = 5 * linediff
    display_text(surface, "Formulas", gfx_data.assets.font_message, (50, y))

    y += 2 * linediff
    display_text(surface, "Vial slots:", gfx_data.assets.font_message, (50, y))
    y += linediff
    for idx, spell in enumerate(spellbuilder.current_slots):
        text = "Slot {}: {}".format(idx, spell.name)
        if idx == spellbuilder.currslot:
            text += "<-- "
        display_text(surface, text, gfx_data.assets.font_message, (50, y))
        y += linediff

    y += 3 * linediff
    display_text(surface, "Spell {}".format(spellbuilder.currspell + 1), gfx_data.assets.font_message, (50, y))
    spells = SpellEngine.evaluate(spellbuilder)
    y += linediff
    display_text(surface,
                 "Spell stats {}".format(spells[spellbuilder.currspell].text_stats), gfx_data.assets.font_message,
                 (50, y))

    y += 3 * linediff
    display_text(surface, "Press Tab for help".format(spellbuilder.currspell + 1), gfx_data.assets.font_message,
                 (50, y))
    gfx_data.main.blit(surface, (200, 200))

def levelup_menu(gfx_data, spellbuilder, menu_data):
    surface = pygame.Surface((800, 600))
    header = [
        "You have expanded your skills and equipment, please choose:",
        ""
    ]
    linediff = 15
    y = 3*linediff
    display_lines(surface, gfx_data.assets.font_message, header, starty=y)

    y += 2*linediff
    choices = [
        "Bigger vials (+1 slot per vial)",
        "More vials (+1 prepared formula)"
    ]
    for idx, choice in enumerate(choices):
        text = choice
        if idx == menu_data.currchoice:
            text += "<--"
        display_text(surface, text, gfx_data.assets.font_message, (50, y))
        y += linediff
    gfx_data.main.blit(surface, (200, 200))

def welcome_menu(gfx_data):
    lines = [
        "Welcome to Formula",
        "",
        "A game of dungeon crawling, potion brewing and vial slinging",
        "",
        "Next you'll be shown the formula screen, press Tab to show help",
        "Escape to cancel actions or quit the current menu, or the game",
        "",
        "Press Escape to continue and choose your formulas"
    ]
    display_menu(gfx_data, lines, (800, 600))


def help_menu(gfx_data):
    lines = [
        "How to play",
        "WASD: to walk around",
        "1-5: Cast vial",
        "E: Interact",
        "You select targets using the mouse",
        "    Throw with left click, cancel with right click",
        "",
        "ESCAPE: Close current screen",
        "TAB: Show help for the current screen"
    ]
    display_menu(gfx_data, lines, (800, 600))


def spellmaker_help_menu(gfx_data):
    lines = [
        "Building spells:",
        "Q,W,E,R,S: Set current slot to ingredient",
        "Up/down arrow: Switch to next/previous slot",
        "Right/left arrow: Switch to next/previous spell",
        "Cooldown is increased for every used slot",
        "",
        "Adding fire to a spell increases damage",
        "Adding life to a spell increases healing",
        "Adding range to a spell makes it reach further",
        "Adding area to a spell gives it wider area of effect"
    ]
    display_menu(gfx_data, lines, (800, 600))
