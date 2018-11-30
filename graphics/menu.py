import pygame

from graphics.display_helpers import display_text, display_lines


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
