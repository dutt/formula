import random
import math

import pygame
import tcod

from components.drawable import Drawable
from components.game_states import GameStates
from graphics.constants import colors, CELL_WIDTH, CELL_HEIGHT
from graphics.display_helpers import display_bar, display_text, display_lines
from graphics.minor_windows import GeneralHelpWindow
from graphics.window import Window
from systems.input_handlers import EventType
from util import Pos, distance
from systems.tutorial import Tutorial


class GameWindow(Window):
    def __init__(self, constants, visible=False, parent=None):
        super().__init__(
            Pos(constants.right_panel_size.width, 0),
            constants.game_window_size,
            visible,
            parent=parent,
        )
        self.show_all = False
        self.drawing_priority = 2

    def draw(self, game_data, gfx_data):
        main = pygame.Surface(self.size.tuple())

        self.calculate_lightmap(game_data, gfx_data)
        self.draw_terrain(game_data, gfx_data, main)
        if game_data.state == GameStates.TARGETING:
            self.draw_targeting_boundary(game_data, gfx_data, main)

        self.draw_entities(game_data, gfx_data, main)
        self.draw_effects(game_data, gfx_data, main)
        self.draw_help(game_data, gfx_data, main)
        if game_data.state == GameStates.TARGETING:
            self.draw_targeting(game_data, gfx_data, main)
        if game_data.state == GameStates.PLAY:
            self.draw_mouse_over_info(game_data, gfx_data, main)
        gfx_data.main.blit(main, self.pos.tuple())

    def calculate_lightmap(self, game_data, gfx_data):
        # first zero all visible light values
        for x in range(gfx_data.camera.x1, gfx_data.camera.x2):
            for y in range(gfx_data.camera.y1, gfx_data.camera.y2):
                visible = tcod.map_is_in_fov(game_data.fov_map, x, y)
                if not visible:
                    continue
                game_data.map.tiles[x][y].light = 0

        # then add brightness for each surrounding tile
        for e in game_data.map.entities:
            if not e.light:
                continue
            for x in range(gfx_data.camera.x1, gfx_data.camera.x2):
                for y in range(gfx_data.camera.y1, gfx_data.camera.y2):
                    visible = tcod.map_is_in_fov(game_data.fov_map, x, y)
                    if not visible:
                        continue
                    distance = int((e.pos - Pos(x, y)).length())
                    distance = max(1, distance)
                    if distance < e.light.brightness:
                        game_data.map.tiles[x][y].light += 60 // distance

    def draw_terrain(self, game_data, gfx_data, main):
        surface = pygame.Surface(
            game_data.constants.game_window_size.tuple(), pygame.SRCALPHA
        )
        surface.fill(colors.BACKGROUND)
        for x in range(gfx_data.camera.x1, gfx_data.camera.x2):
            for y in range(gfx_data.camera.y1, gfx_data.camera.y2):
                visible = tcod.map_is_in_fov(game_data.fov_map, x, y)
                asset = game_data.map.tiles[x][y].get_drawable(self.show_all or visible)
                if visible:
                    game_data.map.tiles[x][y].explored = True

                if asset:
                    distance = (game_data.player.pos - Pos(x, y)).length()
                    if visible:
                        if distance < 3.5:  # 1 range
                            darken = 20
                        elif distance < 5.5:  # 2 range
                            darken = 40
                        elif distance < 7.5:  # 3 range
                            darken = 60
                        else:
                            darken = 80
                    else:
                        darken = 80

                    # if visible:
                    darken -= game_data.map.tiles[x][y].light

                    darken = max(0, min(255, darken))
                    drawable = Drawable(asset)
                    drawable.colorize((darken, darken, darken), pygame.BLEND_RGBA_SUB)
                    sx, sy = gfx_data.camera.map_to_screen(x, y)
                    surface.blit(drawable.asset, (sx * CELL_WIDTH, sy * CELL_HEIGHT))

                    if game_data.map.tiles[x][y].decor:
                        for decor_drawable in game_data.map.tiles[x][y].decor:
                            drawable = Drawable(decor_drawable.asset)
                            drawable.colorize(
                                (darken, darken, darken), pygame.BLEND_RGB_SUB
                            )
                            surface.blit(
                                drawable.asset, (sx * CELL_WIDTH, sy * CELL_HEIGHT)
                            )

                    if game_data.map.tiles[x][y].trap:
                        drawable = Drawable(gfx_data.assets.trap)
                        drawable.colorize(
                            (darken, darken, darken), pygame.BLEND_RGB_SUB
                        )
                        surface.blit(
                            drawable.asset, (sx * CELL_WIDTH, sy * CELL_HEIGHT)
                        )

        main.blit(surface, (0, 0))

    def draw_entities(self, game_data, gfx_data, main):
        rendering_sorted = sorted(
            game_data.map.entities, key=lambda e: e.render_order.value
        )
        for e in rendering_sorted:
            if not e.drawable:
                continue
            if (
                self.show_all
                or tcod.map_is_in_fov(game_data.fov_map, e.pos.x, e.pos.y)
                or (e.stairs and game_data.map.tiles[e.pos.x][e.pos.y].explored)
            ):
                sx, sy = gfx_data.camera.map_to_screen(e.pos.x, e.pos.y)
                main.blit(e.drawable.asset, (sx * CELL_WIDTH, sy * CELL_HEIGHT))
                for ad in e.attached_effects:
                    main.blit(ad.drawable.asset, (sx * CELL_WIDTH, sy * CELL_HEIGHT))

                # health bar for monsters
                bar_height = 6
                if e.fighter and e.ai and e.fighter.hp != e.fighter.max_hp:
                    bar_pos = Pos(
                        sx * CELL_WIDTH, (CELL_HEIGHT - bar_height) + sy * CELL_HEIGHT,
                    )
                    display_bar(
                        main,
                        assets=None,
                        pos=bar_pos,
                        width=CELL_WIDTH,
                        current=e.fighter.hp,
                        maxval=e.fighter.max_hp,
                        color=colors.HP_BAR_FRONT,
                        bgcolor=colors.HP_BAR_BACKGROUND,
                        height=bar_height,
                        text=None,
                        show_numbers=False,
                    )

    def global_screen_pos_to_map_screen_pos(self, x, y, game_data):
        return x - game_data.constants.right_panel_size.width, y

    def map_screen_pos_to_tile(self, x, y, gfx_data):
        rx, ry = x // CELL_WIDTH, y // CELL_HEIGHT
        sx, sy = gfx_data.camera.screen_to_map(rx, ry)
        return sx, sy

    def get_tile_rect(self, x, y, gfx_data):
        tx, ty = gfx_data.camera.map_to_screen(x, y)
        return tx * CELL_WIDTH, ty * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT

    def draw_targeting(self, game_data, gfx_data, main):
        def draw_rect_boundary(surface, colour, rect, draw_cross):
            x1 = rect[0]
            x2 = rect[0] + rect[2]
            y1 = rect[1]
            y2 = rect[1] + rect[3]
            pygame.draw.line(surface, colour, (x1, y1), (x1, y2), 4)
            pygame.draw.line(surface, colour, (x1, y1), (x2, y1), 4)
            pygame.draw.line(surface, colour, (x2, y1), (x2, y2), 4)
            pygame.draw.line(surface, colour, (x1, y2), (x2, y2), 4)
            if draw_cross:
                pygame.draw.line(surface, colour, (x1, y1), (x2, y2), 3)
                pygame.draw.line(surface, colour, (x2, y1), (x1, y2), 3)

        item = None
        if game_data.targeting_formula:
            item = game_data.targeting_formula
        elif game_data.targeting_consumable:
            item = game_data.targeting_consumable
        assert item

        max_dist = item.distance * CELL_WIDTH
        pos = pygame.mouse.get_pos()
        px, py = pos

        targeting_surface = pygame.Surface(
            game_data.constants.window_size.tuple(), pygame.SRCALPHA
        )

        # find targeted tile
        map_screen_pos = self.global_screen_pos_to_map_screen_pos(px, py, game_data)
        tile = self.map_screen_pos_to_tile(
            map_screen_pos[0], map_screen_pos[1], gfx_data
        )

        rect = self.get_tile_rect(tile[0], tile[1], gfx_data)
        rect_center = rect[0] + CELL_WIDTH / 2, rect[1] + CELL_HEIGHT / 2

        # find player position
        s_player_x, s_player_y = gfx_data.camera.map_to_screen(
            game_data.player.pos.x, game_data.player.pos.y
        )
        orig = (s_player_x * CELL_WIDTH, s_player_y * CELL_HEIGHT)
        orig = (orig[0] + CELL_WIDTH / 2, orig[1] + CELL_HEIGHT / 2)  # centered

        dist = distance(orig[0], orig[1], rect_center[0], rect_center[1])

        if dist > max_dist:
            from util import Vec

            vec = Vec(px - orig[0] - self.pos.x, py - orig[1])
            normalized = vec.normalize()
            red_part = (
                orig[0] + normalized.x * max_dist,
                orig[1] + normalized.y * max_dist,
            )
            pygame.draw.line(targeting_surface, (150, 0, 0), orig, red_part)
            pygame.draw.line(targeting_surface, (100, 100, 100), red_part, rect_center)
            draw_rect_boundary(
                targeting_surface, (150, 100, 100), rect, draw_cross=True
            )
        elif item.area == 1:  # no aoe
            pygame.draw.line(targeting_surface, (255, 0, 0), orig, rect_center)
            draw_rect_boundary(targeting_surface, (255, 0, 0), rect, draw_cross=False)
        else:
            pygame.draw.line(main, (255, 0, 0), orig, rect_center)

            for x in range(
                math.ceil(tile[0] - item.distance), math.ceil(tile[0] + item.distance),
            ):
                for y in range(
                    math.ceil(tile[1] - item.distance),
                    math.ceil(tile[1] + item.distance),
                ):
                    dist = math.sqrt((x - tile[0]) ** 2 + (y - tile[1]) ** 2)
                    if dist < item.area:
                        tile_rect = self.get_tile_rect(x, y, gfx_data)
                        draw_rect_boundary(
                            targeting_surface, (255, 0, 0), tile_rect, draw_cross=False,
                        )

        targeting_surface.set_alpha(150)
        main.blit(targeting_surface, (0, 0))

    def draw_targeting_boundary(self, game_data, gfx_data, main):
        # find player position
        s_player_x, s_player_y = gfx_data.camera.map_to_screen(
            game_data.player.pos.x, game_data.player.pos.y
        )
        orig = (s_player_x * CELL_WIDTH, s_player_y * CELL_HEIGHT)
        orig = (orig[0] + CELL_WIDTH / 2, orig[1] + CELL_HEIGHT / 2)  # centered

        item = None
        if game_data.targeting_formula:
            item = game_data.targeting_formula
        elif game_data.targeting_consumable:
            item = game_data.targeting_consumable
        assert item

        for x in range(gfx_data.camera.x1, gfx_data.camera.x2):
            for y in range(gfx_data.camera.y1, gfx_data.camera.y2):
                visible = tcod.map_is_in_fov(game_data.fov_map, x, y)
                asset = game_data.map.tiles[x][y].get_drawable(visible)
                if not asset:
                    continue
                rect = self.get_tile_rect(x, y, gfx_data)
                rect_center = rect[0] + CELL_WIDTH / 2, rect[1] + CELL_HEIGHT / 2
                dist = distance(orig[0], orig[1], rect_center[0], rect_center[1])
                max_dist = item.distance * CELL_WIDTH
                if dist <= max_dist:
                    continue
                drawable = Drawable(asset)
                darken = 100
                drawable.colorize((darken, darken, darken), pygame.BLEND_RGBA_SUB)
                sx, sy = gfx_data.camera.map_to_screen(x, y)
                main.blit(drawable.asset, (sx * CELL_WIDTH, sy * CELL_HEIGHT))

    def draw_effects(self, game_data, gfx_data, main):
        surface = pygame.Surface(
            game_data.constants.window_size.tuple(), pygame.SRCALPHA
        )
        for effect in gfx_data.visuals.effects:
            if not effect.visible:
                continue
            sx, sy = gfx_data.camera.map_to_screen(effect.pos.x, effect.pos.y)
            surface.blit(effect.drawable.asset, (sx * CELL_WIDTH, sy * CELL_HEIGHT))
        main.blit(surface, (0, 0))

    def draw_mouse_over_info(self, game_data, gfx_data, main):
        info_surface = pygame.Surface(
            game_data.constants.window_size.tuple(), pygame.SRCALPHA
        )
        pos = pygame.mouse.get_pos()
        px, py = pos
        map_screen_pos = self.global_screen_pos_to_map_screen_pos(px, py, game_data)
        tile_x, tile_y = self.map_screen_pos_to_tile(
            map_screen_pos[0], map_screen_pos[1], gfx_data
        )
        tile_pos = Pos(tile_x, tile_y)
        names = []
        for e in game_data.map.entities:
            if e.pos == tile_pos and tcod.map_is_in_fov(
                game_data.fov_map, tile_pos.x, tile_pos.y
            ):
                names.append(e.raw_name)
        if not names:
            return
        text = ", ".join(names)
        display_text(
            info_surface,
            text,
            gfx_data.assets.font_message,
            (px - self.pos.x + 20, py),
            text_color=colors.WHITE,
            bg_color=colors.BACKGROUND,
        )
        main.blit(info_surface, (0, 0))

    def draw_help(self, game_data, gfx_data, main):

        help_surface = pygame.Surface(
            game_data.constants.window_size.tuple(), pygame.SRCALPHA
        )

        if not game_data.run_planner.has_next:  # last level
            for e in game_data.map.entities:
                if e.name == "Remains of Arina" and tcod.map_is_in_fov(
                    game_data.fov_map, e.pos.x, e.pos.y
                ):
                    sx, sy = gfx_data.camera.map_to_screen(e.pos.x, e.pos.y)
                    sx, sy = sx * CELL_WIDTH + 40, sy * CELL_HEIGHT
                    display_text(
                        help_surface,
                        "The witch is dead, press E here to verify",
                        gfx_data.assets.font_message,
                        (sx, sy),
                        text_color=colors.WHITE,
                        bg_color=colors.BACKGROUND,
                    )
                    return
        elif not game_data.run_planner.current_map.tutorial:
            return

        messages = Tutorial.get_messages(game_data, gfx_data)
        for msg in messages:
            display_text(
                help_surface,
                msg.text,
                gfx_data.assets.font_message,
                msg.pos.tuple(),
                text_color=colors.WHITE,
                bg_color=colors.BACKGROUND,
            )

        main.blit(help_surface, (0, 0))

    def handle_key(self, game_data, gfx_data, key_action):
        show_help = key_action.get(EventType.show_help)
        if show_help:
            return {EventType.show_window: GeneralHelpWindow}
