import pygame
import tcod
from attrdict import AttrDict

from entity import Pos
from graphics.assets import Assets
from graphics.constants import CELL_HEIGHT, CELL_WIDTH, colors
from game_states import GameStates

def initialize(constants):
    pygame.display.init()
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


def render_bar(surface, assets, pos, width, current, maxval, color, bgcolor, height=30, text=None):
    current_length = max(0, (current / maxval) * width)
    pygame.draw.rect(surface, bgcolor, pygame.Rect(pos.x, pos.y, width, height))
    pygame.draw.rect(surface, color, pygame.Rect(pos.x, pos.y, current_length, height))
    msg = "{}/{}".format(current, maxval)
    display_text(surface, msg, assets.font_message, (pos.x + 10, pos.y + 5))


def render_all(gfx_data, game_data, targeting_spell, spellbuilder):
    gfx_data.main.fill(game_data.constants.colors.dark_wall)
    assets = Assets()
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
                        # main.blit(assets.undead_sheet.get_image(x, y)[0],
                        main.blit(assets.light_wall[0],
                                  (panel_width + x * CELL_WIDTH,
                                   y * CELL_HEIGHT))
                else:
                    if wall:
                        main.blit(assets.dark_wall[0],
                                  (panel_width + x * CELL_WIDTH,
                                   y * CELL_HEIGHT))

    def draw_entities():
        for e in game_data.entities:
            if e.drawable:
                print(e)
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
        display_text(main, "Spells", assets.font_title, (10, 20))
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

    def draw_targeting():
        if game_data.state == GameStates.TARGETING:
            pass

    draw_terrain()
    draw_entities()
    draw_bottom_panel()
    draw_right_panel()
    draw_targeting()

    # pygame.draw.rect(gfx_data.main, (0, 128, 255), pygame.Rect(30, 30, 60, 60))

    pygame.display.flip()
