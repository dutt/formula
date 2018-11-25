import math
import textwrap

import pygame
import tcod

import util
from game_states import GameStates
from graphics.assets import Assets
from graphics.camera import Camera
from graphics.constants import CELL_HEIGHT, CELL_WIDTH, colors
from graphics.visual_effect import VisualEffectSystem
from util import Pos


class GfxState:
    def __init__(self, main, assets, camera, fullscreen, visuals, fps_per_second, clock):
        self.main = main
        self.assets = assets
        self.camera = camera
        self.fullscreen = fullscreen
        self.visuals = visuals
        self.fps_per_second = fps_per_second
        self.clock = clock


def initialize_gfx(constants):
    pygame.init()
    pygame.display.set_caption("Formulas")
    pygame.mixer.quit()
    main = pygame.display.set_mode((constants.window_size.width, constants.window_size.height))
    assets = Assets()
    camera = Camera(constants.camera_size.width, constants.camera_size.height, constants.map_size)
    fps_per_second = 30
    visuals = VisualEffectSystem(fps_per_second)
    clock = pygame.time.Clock()
    return GfxState(
            main=main,
            assets=assets,
            camera=camera,
            fullscreen=False,
            visuals=visuals,
            fps_per_second=fps_per_second,
            clock=clock
    )


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


def display_lines(surface, font, lines, x=50, starty=50, ydiff=20):
    y = starty
    for line in lines:
        display_text(surface, line, font, (x, y))
        y += ydiff


def display_menu(gfx_data, lines, size, surface=None):
    has_surface=surface is not None
    if not has_surface:
        surface = pygame.Surface(size)
    display_lines(surface, gfx_data.assets.font_message, lines)
    if not has_surface:
        gfx_data.main.blit(surface, (200, 200))


def render_bar(surface, assets, pos, width, current, maxval, color, bgcolor, height=30, text=None):
    current_length = max(0, (current / maxval) * width)
    pygame.draw.rect(surface, bgcolor, pygame.Rect(pos.x, pos.y, width, height))
    pygame.draw.rect(surface, color, pygame.Rect(pos.x, pos.y, current_length, height))
    msg = "{}/{}".format(current, maxval)
    display_text(surface, msg, assets.font_message, (pos.x + 10, pos.y + 5))


last_tile = None


def render_all(gfx_data, game_data, targeting_formula, formulabuilder, menu_data):
    gfx_data.main.fill(game_data.constants.colors.dark_wall)
    assets = gfx_data.assets
    panel_width = game_data.constants.right_panel_size.width
    main = gfx_data.main

    def draw_terrain():
        # for x in range(30):
        #    for y in range(15):
        #        #main.blit(assets.effect0_sheet.get_image(x, 15+y)[0],
        #        main.blit(assets.shield_effect[0],
        #                  (x * CELL_WIDTH, y* CELL_HEIGHT))
        # return
        for x in range(gfx_data.camera.x1, gfx_data.camera.x2):
            for y in range(gfx_data.camera.y1, gfx_data.camera.y2):
                wall = game_data.map.tiles[x][y].block_sight
                visible = tcod.map_is_in_fov(game_data.fov_map, x, y)
                sx, sy = gfx_data.camera.map_to_screen(x, y)
                # visible = True
                if visible:
                    if wall:
                        main.blit(assets.light_wall[0],
                                  (panel_width + sx * CELL_WIDTH,
                                   sy * CELL_HEIGHT))
                    else:
                        main.blit(assets.light_floor[0],
                                  (panel_width + sx * CELL_WIDTH,
                                   sy * CELL_HEIGHT))
                    game_data.map.tiles[x][y].explored = True
                elif game_data.map.tiles[x][y].explored:
                    if wall:
                        main.blit(assets.dark_wall[0],
                                  (panel_width + sx * CELL_WIDTH,
                                   sy * CELL_HEIGHT))
                    else:
                        main.blit(assets.dark_floor[0],
                                  (panel_width + sx * CELL_WIDTH,
                                   sy * CELL_HEIGHT))

    def draw_entities():
        rendering_sorted = sorted(game_data.entities, key=lambda e: e.render_order.value)
        for e in rendering_sorted:
            if e.drawable and tcod.map_is_in_fov(game_data.fov_map, e.pos.x, e.pos.y):
                sx, sy = gfx_data.camera.map_to_screen(e.pos.x, e.pos.y)
                main.blit(e.drawable.asset[0],
                          (panel_width + sx * CELL_WIDTH,
                           sy * CELL_HEIGHT))
                for ad in e.attached_effects:
                    main.blit(ad.drawable.asset[0],
                              (panel_width + sx * CELL_WIDTH,
                               sy * CELL_HEIGHT))

    def draw_message_log():
        y = 800
        messages = game_data.log.messages
        for idx, msg in enumerate(messages[-9:]):
            display_text(main, msg.text, assets.font_message, (180, y + idx * 20), msg.color)

    def draw_bottom_panel():
        draw_message_log()

    def draw_right_panel():
        surface = pygame.Surface((game_data.constants.right_panel_size.width, game_data.constants.window_size.height))
        surface.fill(game_data.constants.colors.dark_wall)

        y = 20
        render_bar(surface, assets, Pos(10, y), 100, game_data.player.fighter.hp, game_data.player.fighter.max_hp,
                   (160, 0, 0), (100, 0, 0))

        if game_data.player.fighter.shield:
            y += 30
            render_bar(surface, assets, Pos(10, y), 100, game_data.player.fighter.shield.level,
                       game_data.player.fighter.shield.max_level,
                       (0, 160, 0), (0, 100, 0))

        y += 50
        display_text(surface, "Formulas", assets.font_title, (10, y))
        player = game_data.player
        y += 30
        for idx, formula in enumerate(player.caster.formulas):
            if player.caster.is_on_cooldown(idx):
                render_bar(surface, assets, Pos(20, y + idx * 20), 80, player.caster.get_cooldown(idx),
                           formula.cooldown,
                           (0, 127, 255), colors.BLACK)

            else:
                msg = "{}: {}".format(idx + 1, formula.text_repr)
                display_text(surface, msg, assets.font_message, (10, y + idx * 20))
            y += 40

        main.blit(surface, (0, 0))

    def global_screen_pos_to_map_screen_pos(x, y):
        return x - panel_width, y

    def map_screen_pos_to_tile(x, y):
        rx, ry = x // CELL_WIDTH, y // CELL_HEIGHT
        sx, sy = gfx_data.camera.screen_to_map(rx, ry)
        return sx, sy

    def get_tile_rect(x, y):
        tx, ty = gfx_data.camera.map_to_screen(x, y)
        return panel_width + tx * CELL_WIDTH, ty * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT

    def draw_targeting():
        max_dist = targeting_formula.distance * CELL_WIDTH
        pos = pygame.mouse.get_pos()
        targeting_surface = pygame.Surface(game_data.constants.window_size.tuple(), pygame.SRCALPHA)

        # find targeted tile
        map_screen_pos = global_screen_pos_to_map_screen_pos(pos[0], pos[1])
        tile = map_screen_pos_to_tile(map_screen_pos[0], map_screen_pos[1])

        rect = get_tile_rect(tile[0], tile[1])
        rect_center = rect[0] + CELL_WIDTH / 2, rect[1] + CELL_HEIGHT / 2

        # find player position
        s_player_x, s_player_y = gfx_data.camera.map_to_screen(game_data.player.pos.x, game_data.player.pos.y)
        orig = (panel_width + s_player_x * CELL_WIDTH, s_player_y * CELL_HEIGHT)
        orig = (orig[0] + CELL_WIDTH / 2, orig[1] + CELL_HEIGHT / 2)  # centered

        dist = util.distance(orig[0], orig[1], rect_center[0], rect_center[1])

        # global last_tile
        # if not last_tile or tile != last_tile:
        #    print("pos: {}, map_screen_pos {}".format(pos, map_screen_pos))
        #    print("tile {}, player {}".format(tile, game_data.player.pos))
        #    rx, ry = map_screen_pos[0] // CELL_WIDTH, map_screen_pos[1] // CELL_HEIGHT
        #    print("rx {}, ry {}".format(rx, ry))
        #    sx, sy = gfx_data.camera.screen_to_map(rx, ry)
        #    print("sx {}, sy {}".format(sx, sy))
        #    last_tile = tile

        if dist > max_dist:
            vec = (pos[0] - orig[0], pos[1] - orig[1])
            length = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
            normalized = (vec[0] / length, vec[1] / length)
            partial_dist = (max_dist / dist) * dist
            red_part = (orig[0] + normalized[0] * partial_dist, orig[1] + normalized[1] * partial_dist)
            pygame.draw.line(targeting_surface, (255, 0, 0), orig, red_part)
            pygame.draw.line(targeting_surface, (150, 100, 100), red_part, rect_center)
            pygame.draw.rect(targeting_surface, (150, 100, 100), rect)
        elif targeting_formula.area == 1:  # no aoe
            pygame.draw.line(targeting_surface, (255, 0, 0), orig, rect_center)
            pygame.draw.rect(targeting_surface, (255, 0, 0), rect)
        else:
            pygame.draw.line(main, (255, 0, 0), orig, rect_center)

            for x in range(math.ceil(tile[0] - targeting_formula.distance),
                           math.ceil(tile[0] + targeting_formula.distance)):
                for y in range(math.ceil(tile[1] - targeting_formula.distance),
                               math.ceil(tile[1] + targeting_formula.distance)):
                    dist = (math.sqrt((x - tile[0]) ** 2 + (y - tile[1]) ** 2))
                    if dist < targeting_formula.area:
                        tile_rect = get_tile_rect(x, y)
                        pygame.draw.rect(targeting_surface, (255, 0, 0), tile_rect)
        targeting_surface.set_alpha(150)
        gfx_data.main.blit(targeting_surface, (0, 0))

    def draw_effects():
        surface = pygame.Surface(game_data.constants.window_size.tuple(), pygame.SRCALPHA)
        for effect in gfx_data.visuals.effects:
            sx, sy = gfx_data.camera.map_to_screen(effect.pos.x, effect.pos.y)
            surface.blit(effect.drawable.asset[0],
                         (panel_width + sx * CELL_WIDTH,
                          sy * CELL_HEIGHT))
        gfx_data.main.blit(surface, (0, 0))

    draw_bottom_panel()
    draw_right_panel()
    draw_terrain()
    draw_entities()
    draw_effects()
    if game_data.state == GameStates.TARGETING:
        draw_targeting()

    if game_data.state == GameStates.WELCOME_SCREEN:
        welcome_menu(gfx_data)
    elif game_data.state == GameStates.GENERAL_HELP_SCREEN:
        help_menu(gfx_data)
    elif game_data.state == GameStates.FORMULA_SCREEN:
        formula_menu(gfx_data, formulabuilder)
    elif game_data.state == GameStates.FORMULA_HELP_SCEEN:
        formula_help_menu(gfx_data)
    elif game_data.state == GameStates.LEVEL_UP:
        levelup_menu(gfx_data, menu_data)
    elif game_data.state == GameStates.STORY_SCREEN:
        story_screen(gfx_data, game_data.story)
    elif game_data.state == GameStates.STORY_HELP_SCREEN:
        story_screen_help(gfx_data)
    elif game_data.state == GameStates.VICTORY:
        story_screen(gfx_data, game_data.story)
    pygame.display.flip()


def story_screen(gfx_data, story_data):
    surface = pygame.Surface((800, 600))
    page_lines = story_data.current_page.split("\n")
    lines = []
    for pl in page_lines:
        if pl == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(pl, 60))
    display_menu(gfx_data, lines, (800, 600), surface=surface)
    display_text(surface, "{}/{}".format(story_data.page_num, story_data.page_count),
                 gfx_data.assets.font_message, (40, 400))
    gfx_data.main.blit(surface, (200, 200))


def story_screen_help(gfx_data):
    lines = [
        "This is the next page of the story",
        "",
        "Press Space for the next page",
        "Press Escape or Tab to go back",
    ]
    display_menu(gfx_data, lines, (800, 600))


def formula_menu(gfx_data, formulabuilder):
    surface = pygame.Surface((800, 600))
    linediff = 12
    y = 5 * linediff
    display_text(surface, "Formulas", gfx_data.assets.font_message, (50, y))

    y += 2 * linediff
    display_text(surface, "Vial slots:", gfx_data.assets.font_message, (50, y))
    y += linediff
    for idx, formula in enumerate(formulabuilder.current_slots):
        text = "Slot {}: {}".format(idx, formula.name)
        if idx == formulabuilder.currslot:
            text += "<-- "
        display_text(surface, text, gfx_data.assets.font_message, (50, y))
        y += linediff

    y += 3 * linediff
    display_text(surface, "Formula {}".format(formulabuilder.currformula + 1), gfx_data.assets.font_message, (50, y))
    formulas = formulabuilder.evaluate()
    y += linediff
    display_text(surface,
                 "Formula stats:",
                 gfx_data.assets.font_message,
                 (50, y))
    y += linediff
    lines = textwrap.wrap(formulas[formulabuilder.currformula].text_stats, 60)
    display_lines(surface, gfx_data.assets.font_message, lines, 50, y, ydiff=10)
    y += len(lines) * linediff

    y += 6 * linediff
    display_text(surface, "Press Tab for help".format(formulabuilder.currformula + 1), gfx_data.assets.font_message,
                 (50, y))
    gfx_data.main.blit(surface, (200, 200))


def levelup_menu(gfx_data, menu_data):
    surface = pygame.Surface((800, 600))
    header = [
        "You have expanded your skills and equipment, please choose:",
        ""
    ]
    linediff = 15
    y = 3 * linediff
    display_lines(surface, gfx_data.assets.font_message, header, starty=y)

    y += 2 * linediff
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
        "Press Escape to continue"
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


def formula_help_menu(gfx_data):
    lines = [
        "Building formulas:",
        "Q,W,E,R,A,S, D: Set current slot to ingredient",
        "Up/down arrow: Switch to next/previous slot",
        "Right/left arrow: Switch to next/previous formula",
        "Cooldown is increased for every used slot",
        "",
        "Adding fire to a formula increases damage",
        "Adding life to a formula increases healing",
        "Adding range to a formula makes it reach further",
        "Adding area to a formula gives it wider area of effect"
    ]
    display_menu(gfx_data, lines, (800, 600))
