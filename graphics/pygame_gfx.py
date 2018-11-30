import math

import pygame
import tcod

import util
from game_states import GameStates
from graphics.assets import Assets
from graphics.camera import Camera
from graphics.constants import CELL_HEIGHT, CELL_WIDTH, colors
from graphics.display_helpers import display_text
from graphics.menu import story_screen_help, story_screen, formula_help_menu, formula_menu, help_menu, levelup_menu, \
    welcome_menu
from graphics.visual_effect import VisualEffectSystem
from util import Pos
from graphics.window import WindowManager, RightPanelWindow, MessageLogWindow

class stuff:
    pass

class GfxState:
    def __init__(self, main, assets, camera, fullscreen, visuals, fps_per_second, clock, windows):
        self.main = main
        self.assets = assets
        self.camera = camera
        self.fullscreen = fullscreen
        self.visuals = visuals
        self.fps_per_second = fps_per_second
        self.clock = clock
        self.windows = windows


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
    windows = WindowManager()
    windows.push(RightPanelWindow(constants))
    windows.push(MessageLogWindow(constants))
    return GfxState(
            main=main,
            assets=assets,
            camera=camera,
            fullscreen=False,
            visuals=visuals,
            fps_per_second=fps_per_second,
            clock=clock,
            windows=windows
    )


from components.drawable import Drawable


def render_all(gfx_data, game_data, targeting_formula, formulabuilder, menu_data):
    gfx_data.main.fill(colors.BACKGROUND)
    assets = gfx_data.assets
    panel_width = game_data.constants.right_panel_size.width
    main = gfx_data.main

    def draw_terrain():
        surface = pygame.Surface(game_data.constants.window_size.tuple(), pygame.SRCALPHA)

        # for x in range(30):
        #    for y in range(15):
        #        #main.blit(assets.effect0_sheet.get_image(x, 15+y)[0],
        #        main.blit(assets.shield_effect[0],
        #                  (x * CELL_WIDTH, y* CELL_HEIGHT))
        # return
        for x in range(gfx_data.camera.x1, gfx_data.camera.x2):
            for y in range(gfx_data.camera.y1, gfx_data.camera.y2):
                if x >= game_data.map.width or y >= game_data.map.height:
                    continue
                wall = game_data.map.tiles[x][y].block_sight
                wall_type = game_data.map.tiles[x][y].wall_info
                floor_type = game_data.map.tiles[x][y].floor_info
                visible = tcod.map_is_in_fov(game_data.fov_map, x, y)
                sx, sy = gfx_data.camera.map_to_screen(x, y)
                # visible = True
                if visible:
                    distance = game_data.player.pos - Pos(x, y)
                    if distance.length() > 5:
                        darken = (distance.length() - 3) * 10
                    else:
                        darken = 0
                    if wall:
                        asset = assets.light_wall[wall_type]
                    else:
                        asset = assets.light_floor[floor_type]
                    drawable = Drawable(asset)
                    drawable.colorize((darken, darken, darken), pygame.BLEND_RGBA_SUB)
                    surface.blit(drawable.asset[0],
                                 (panel_width + sx * CELL_WIDTH,
                                  sy * CELL_HEIGHT))
                    game_data.map.tiles[x][y].explored = True
                elif game_data.map.tiles[x][y].explored:
                    if wall:
                        surface.blit(assets.dark_wall[wall_type][0],
                                     (panel_width + sx * CELL_WIDTH,
                                      sy * CELL_HEIGHT))
                    else:
                        surface.blit(assets.dark_floor[floor_type][0],
                                     (panel_width + sx * CELL_WIDTH,
                                      sy * CELL_HEIGHT))
        surface.set_alpha(150)
        gfx_data.main.blit(surface, (0, 0))

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

    def draw_gui():
        gfx_data.windows.draw(game_data, gfx_data)

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
            if not effect.visible:
                continue
            sx, sy = gfx_data.camera.map_to_screen(effect.pos.x, effect.pos.y)
            surface.blit(effect.drawable.asset[0],
                         (panel_width + sx * CELL_WIDTH,
                          sy * CELL_HEIGHT))
        gfx_data.main.blit(surface, (0, 0))

    draw_bottom_panel()
    draw_gui()
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
