import pygame
import tcod
from attrdict import AttrDict

from graphics.assets import Assets
from graphics.constants import CELL_HEIGHT, CELL_WIDTH


def initialize(constants):
    pygame.display.init()
    main = pygame.display.set_mode((constants.window_size.width, constants.window_size.height))
    assets = Assets()
    return AttrDict({
        "main": main,
        "assets": assets
    })


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
                #visible = True
                if visible:
                    if wall:
                        #main.blit(assets.undead_sheet.get_image(x, y)[0],
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

    def draw_bottom_panel():
        total_length = 100
        current_length = max(0, (game_data.player.fighter.hp / game_data.player.fighter.max_hp) * 100)
        pygame.draw.rect(main, (80, 0, 0), pygame.Rect(50, 900, total_length, 30))
        pygame.draw.rect(main, (120, 0, 0), pygame.Rect(50, 900, current_length, 30))

    draw_terrain()
    draw_entities()
    draw_bottom_panel()

    # pygame.draw.rect(gfx_data.main, (0, 128, 255), pygame.Rect(30, 30, 60, 60))


    pygame.display.flip()
