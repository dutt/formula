import tcod

from spell_engine import SpellEngine

def menu(con, header, options, width, screen_size):
    if len(options) > 26: raise ValueError("Can't have more than 26 options in a menu")

    header_height = tcod.console_get_height_rect(con, 0, 0, width, screen_size.height, header)
    height = len(options) + header_height

    window = tcod.console_new(width, height)

    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option in options:
        text = '(' + chr(letter_index) + ')' + option
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    x = int(screen_size.width / 2 - width / 2)
    y = int(screen_size.height / 2 - height / 2)
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def spellmaker_menu(spellbuilder, menu_screen_size, screen_size):
    window = tcod.console_new(menu_screen_size.width, menu_screen_size.height)

    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(window, 0, 1, menu_screen_size.width, menu_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "Spellmaker menu")
    tcod.console_print_ex(window, 0, 2, tcod.BKGND_NONE, tcod.LEFT, "Slots:")

    line = 3
    for idx, s in enumerate(spellbuilder.current_slots):
        text = "Slot {}: {}".format(idx, s.name)
        if idx == spellbuilder.currslot:
            text += " <-"
        tcod.console_print_ex(window, 0, idx + line, tcod.BKGND_SET, tcod.LEFT, text)

    line += len(spellbuilder.current_slots) + 1
    tcod.console_print_ex(window, 0, line, tcod.BKGND_SET, tcod.LEFT, "Spell {}".format(spellbuilder.currspell + 1))
    line += 1
    spells = SpellEngine.evaluate(spellbuilder)
    tcod.console_print_ex(window, 0, line, tcod.BKGND_SET, tcod.LEFT,
                          "Spell {}".format(spells[spellbuilder.currspell].text_stats))

    x = screen_size.width // 2 - menu_screen_size.width // 2
    y = screen_size.height // 2 - menu_screen_size.height // 2

    tcod.console_blit(window, 0, 0, menu_screen_size.width, menu_screen_size.height, 0, x, y, 1.0, 1.0)


def spellmaker_help_menu(screen_size):
    lines = [
        "Building spells:",
        "Q,W,E,R,A,S,D: Set current slot to ingredient",
        "Up/down arrow: Switch to next/previous slot",
        "Right/left arrow: Switch to next/previous spell",
        "Cooldown is increased for every used slot",
        "",
        "Adding fire to a spell increases damage",
        "Adding life to a spell increases healing",
        "Adding range to a spell makes it reach further",
        "Adding area to a spell gives it wider area of effect"
    ]
    show_lines(screen_size, lines)

def level_up_menu(con, header, player, menu_width, screen_size):
    options = ["More HP (+20 hp from {})".format(player.fighter.max_hp),
               "One more slot",
               "One more spell"
               ]
    menu(con, header, options, menu_width, screen_size)


def character_screen(player, character_screen_size, screen_size):
    window = tcod.console_new(character_screen_size.width, character_screen_size.height)

    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(window, 0, 1, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "Character information")
    tcod.console_print_rect_ex(window, 0, 2, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "Level {}".format(player.level.current_level))
    tcod.console_print_rect_ex(window, 0, 3, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "XP {}".format(player.level.current_xp))
    tcod.console_print_rect_ex(window, 0, 4, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "XP to next level {}".format(player.level.xp_to_next_level))
    tcod.console_print_rect_ex(window, 0, 5, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "")

    x = screen_size.width // 2 - character_screen_size.width // 2
    y = screen_size.height // 2 - character_screen_size.height // 2
    tcod.console_blit(window, 0, 0, character_screen_size.width, character_screen_size.height, 0, x, y, 1.0, 0.7)


def show_lines(screen_size, lines):
    window = tcod.console_new(screen_size.width, screen_size.height)

    tcod.console_set_default_foreground(window, tcod.white)
    for idx, line in enumerate(lines):
        tcod.console_print_rect_ex(window, 0, idx + 1, screen_size.width, screen_size.height, tcod.BKGND_SET,
                                   tcod.LEFT, line)

    x = screen_size.width // 10
    y = screen_size.height // 10
    tcod.console_blit(window, 0, 0, screen_size.width, screen_size.height, 0, x, y, 1.0, 0.7)

def welcome_screen(screen_size):
    lines = [
        "Welcome to spellmaker",
        "",
        "A game of dungeon crawling and spellcrafting",
        "Next you'll be shown the spellmaker screen:",
        "",
        "Escape to cancel actions or quit the current menu, or the game",
        "Tab to show help"
    ]
    show_lines(screen_size, lines)

def help_screen(screen_size):
    lines = [
        "How to play",
        "WASD: to walk around",
        "1-5: Cast spell",
        "E: Interact",
        "You select targets using the mouse",
        "    Cast with left click, cancel with right click",
        "",
        "ESCAPE: Close current screen",
        "TAB: Show help for the current screen"
    ]
    show_lines(screen_size, lines)

def main_menu(con, background_image, screen_size):
    tcod.image_blit_2x(background_image, 0, 0, 0)

    tcod.console_set_default_foreground(0, tcod.light_yellow)
    tcod.console_print_ex(0, int(screen_size.width / 2), int(screen_size.height / 2) - 4, tcod.BKGND_NONE, tcod.CENTER,
                          "Spellmaker")
    tcod.console_print_ex(0, int(screen_size.width / 2), int(screen_size.height / 2), tcod.BKGND_NONE, tcod.CENTER,
                          "by dutt")

    menu(con, "", ["Play a new game", "Quit"], 24, screen_size)
