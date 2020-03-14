def get_width(font):
    """Measures the width in pixels of a specified font.

    This method is used when you need the width of a font object.  Most often
    this is useful when designing UI elements where the exact width of a font
    needs to be known.

    Args:
        font (pygame.font.Font): the font whose width is desired.

    Returns:
        font_rect.width (int): the width, in pixels, of the font.

    """

    # render the font out
    font_rect = font.render("a", False, (0, 0, 0)).get_rect()

    return font_rect.width


def get_height(font):
    """Measures the height in pixels of a specified font.

    This method is used when you need the height of a font object.  Most often
    this is useful when designing UI elements where the exact height of a font
    needs to be known.

    Args:
        font (pygame.font.Font): the font whose height is desired.

    Returns:
        font_rect.height (int): the height, in pixels, of the font.

    """

    # render the font out
    font_rect = font.render("a", False, (0, 0, 0)).get_rect()

    return font_rect.height
