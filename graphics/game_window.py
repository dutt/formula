import math

import pygame
import tcod

from components.drawable import Drawable
from game_states import GameStates
from graphics.constants import colors, CELL_WIDTH, CELL_HEIGHT
from graphics.minor_windows import GeneralHelpWindow
from graphics.window import Window
from input_handlers import Event
from util import Pos, distance


class GameWindow(Window):
    def __init__(self, constants, visible):
        super().__init__(Pos(constants.right_panel_size.width, 0), constants.game_window_size, visible)

    def draw(self, game_data, gfx_data):
        if not self.visible:
            return False
        main = pygame.Surface(self.size.tuple())

        gfx_data.main.fill(colors.YELLOW)
        assets = gfx_data.assets

        def draw_terrain():
            surface = pygame.Surface(game_data.constants.game_window_size.tuple(), pygame.SRCALPHA)
            surface.fill(colors.BACKGROUND)
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
                                     (sx * CELL_WIDTH,
                                      sy * CELL_HEIGHT))
                        game_data.map.tiles[x][y].explored = True
                    elif game_data.map.tiles[x][y].explored:
                        if wall:
                            surface.blit(assets.dark_wall[wall_type][0],
                                         (sx * CELL_WIDTH,
                                          sy * CELL_HEIGHT))
                        else:
                            surface.blit(assets.dark_floor[floor_type][0],
                                         (sx * CELL_WIDTH,
                                          sy * CELL_HEIGHT))
            main.blit(surface, (0, 0))

        def draw_entities():
            rendering_sorted = sorted(game_data.entities, key=lambda e: e.render_order.value)
            for e in rendering_sorted:
                if e.drawable and tcod.map_is_in_fov(game_data.fov_map, e.pos.x, e.pos.y):
                    sx, sy = gfx_data.camera.map_to_screen(e.pos.x, e.pos.y)
                    main.blit(e.drawable.asset[0],
                              (sx * CELL_WIDTH,
                               sy * CELL_HEIGHT))
                    for ad in e.attached_effects:
                        main.blit(ad.drawable.asset[0],
                                  (sx * CELL_WIDTH,
                                   sy * CELL_HEIGHT))

        def global_screen_pos_to_map_screen_pos(x, y):
            return x - game_data.constants.right_panel_size.width, y
            # return x, y

        def map_screen_pos_to_tile(x, y):
            rx, ry = x // CELL_WIDTH, y // CELL_HEIGHT
            sx, sy = gfx_data.camera.screen_to_map(rx, ry)
            return sx, sy

        def get_tile_rect(x, y):
            tx, ty = gfx_data.camera.map_to_screen(x, y)
            return tx * CELL_WIDTH, ty * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT

        def draw_targeting():
            max_dist = game_data.targeting_formula.distance * CELL_WIDTH
            pos = pygame.mouse.get_pos()
            px, py = pos

            targeting_surface = pygame.Surface(game_data.constants.window_size.tuple(), pygame.SRCALPHA)

            # find targeted tile
            map_screen_pos = global_screen_pos_to_map_screen_pos(px, py)
            tile = map_screen_pos_to_tile(map_screen_pos[0], map_screen_pos[1])

            rect = get_tile_rect(tile[0], tile[1])
            rect_center = rect[0] + CELL_WIDTH / 2, rect[1] + CELL_HEIGHT / 2

            # find player position
            s_player_x, s_player_y = gfx_data.camera.map_to_screen(game_data.player.pos.x, game_data.player.pos.y)
            orig = (s_player_x * CELL_WIDTH, s_player_y * CELL_HEIGHT)
            orig = (orig[0] + CELL_WIDTH / 2, orig[1] + CELL_HEIGHT / 2)  # centered

            dist = distance(orig[0], orig[1], rect_center[0], rect_center[1])

            if dist > max_dist:
                vec = (px - orig[0], py - orig[1])
                length = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
                normalized = (vec[0] / length, vec[1] / length)
                partial_dist = (max_dist / dist) * dist
                red_part = (orig[0] + normalized[0] * partial_dist, orig[1] + normalized[1] * partial_dist)
                pygame.draw.line(targeting_surface, (255, 0, 0), orig, red_part)
                pygame.draw.line(targeting_surface, (150, 100, 100), red_part, rect_center)
                pygame.draw.rect(targeting_surface, (150, 100, 100), rect)
            elif game_data.targeting_formula.area == 1:  # no aoe
                pygame.draw.line(targeting_surface, (255, 0, 0), orig, rect_center)
                pygame.draw.rect(targeting_surface, (255, 0, 0), rect)
            else:
                pygame.draw.line(main, (255, 0, 0), orig, rect_center)

                for x in range(math.ceil(tile[0] - game_data.targeting_formula.distance),
                               math.ceil(tile[0] + game_data.targeting_formula.distance)):
                    for y in range(math.ceil(tile[1] - game_data.targeting_formula.distance),
                                   math.ceil(tile[1] + game_data.targeting_formula.distance)):
                        dist = (math.sqrt((x - tile[0]) ** 2 + (y - tile[1]) ** 2))
                        if dist < game_data.targeting_formula.area:
                            tile_rect = get_tile_rect(x, y)
                            pygame.draw.rect(targeting_surface, (255, 0, 0), tile_rect)
            targeting_surface.set_alpha(150)
            main.blit(targeting_surface, (0, 0))

        def draw_effects():
            surface = pygame.Surface(game_data.constants.window_size.tuple(), pygame.SRCALPHA)
            for effect in gfx_data.visuals.effects:
                if not effect.visible:
                    continue
                sx, sy = gfx_data.camera.map_to_screen(effect.pos.x, effect.pos.y)
                surface.blit(effect.drawable.asset[0],
                             (sx * CELL_WIDTH,
                              sy * CELL_HEIGHT))
            main.blit(surface, (0, 0))

        draw_terrain()
        draw_entities()
        draw_effects()
        if game_data.state == GameStates.TARGETING:
            draw_targeting()

        gfx_data.main.blit(main, self.pos.tuple())
        return True

    def handle_key(self, game_data, gfx_data, key_action):
        show_help = key_action.get(Event.show_help)
        if show_help:
            return {Event.show_window: GeneralHelpWindow}
