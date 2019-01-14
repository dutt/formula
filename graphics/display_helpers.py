import pygame

from graphics.constants import colors


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
    has_surface = surface is not None
    if not has_surface:
        surface = pygame.Surface(size)
    display_lines(surface, gfx_data.assets.font_message, lines)
    if not has_surface:
        gfx_data.main.blit(surface, (200, 200))


def display_bar(surface, assets, pos, width, current, maxval, color, bgcolor, height=30, text=None, show_numbers=True):
    current_length = max(0, (current / maxval) * width)
    pygame.draw.rect(surface, bgcolor, pygame.Rect(pos.x, pos.y, width, height))
    pygame.draw.rect(surface, color, pygame.Rect(pos.x, pos.y, current_length, height))
    if show_numbers:
        if text and len(text.strip()) > 0:
            msg = "{} {}/{}".format(text, current, maxval)
        else:
            msg = "{}/{}".format(current, maxval)
        display_text(surface, msg, assets.font_message, (pos.x + 10, pos.y + 5))
