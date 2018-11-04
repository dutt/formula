import tcod

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
        tcod.console_print_ex(window, 0, idx+line, tcod.BKGND_SET, tcod.LEFT, "Slot {}: {}".format(idx, s.name))

    line += len(spellbuilder.current_slots) + 1
    tcod.console_print_ex(window, 0, line, tcod.BKGND_SET, tcod.LEFT, "Spell {}".format(spellbuilder.currspell+1))

    x = screen_size.width // 2 - menu_screen_size.width // 2
    y = screen_size.height // 2 - menu_screen_size.height // 2

    tcod.console_blit(window, 0, 0, menu_screen_size.width, menu_screen_size.height, 0, x, y, 1.0, 1.0)

def inventory_menu(con, header, player, width, screen_size):
    if len(player.inventory.items) == 0:
        options = ['inventory is empty']
    else:
        options = []
        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append("{} on main hand".format(item.name))
            elif player.equipment.off_hand == item:
                options.append("{} on off hand".format(item.name))
            else:
                options.append(item.name)

    menu(con, header, options, width, screen_size)

def level_up_menu(con, header, player, menu_width, screen_size):
    options = ["Constitution (+20 hp from {})".format(player.fighter.max_hp),
               "Stregth (+1 attack from {})".format(player.fighter.power),
               "Agility (+1 defense from {})".format(player.fighter.defense),
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
                               tcod.LEFT, "Max HP: {}".format(player.fighter.max_hp))
    tcod.console_print_rect_ex(window, 0, 6, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "Attack {}".format(player.fighter.power))
    tcod.console_print_rect_ex(window, 0, 7, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "Defense {}".format(player.fighter.defense))
    tcod.console_print_rect_ex(window, 0, 8, character_screen_size.width, character_screen_size.height, tcod.BKGND_SET,
                               tcod.LEFT, "")

    x = screen_size.width //2 - character_screen_size.width // 2
    y = screen_size.height //2 - character_screen_size.height // 2
    tcod.console_blit(window, 0, 0, character_screen_size.width, character_screen_size.height, 0, x, y, 1.0, 0.7)

def help_screen(screen_size):
    window = tcod.console_new(screen_size.width, screen_size.height)

    lines = [
      "How to play",
      "Arrow keys: to walk around",
      "G: pick up",
      "M: spellmaker screen",
      "    number keys 1,2,3: select slot",
      "    Q,W,E: set ingredient for current slot",
      "    TAB: next spell",
      "Z: wait",
      "I: inventory",
      "    Press the character next to the line to use or equip",
      "D: drop",
      "ESCAPE: Close current screen",
      "TAB: Show this menu"
    ]
    tcod.console_set_default_foreground(window, tcod.white)
    for idx, line in enumerate(lines):
      tcod.console_print_rect_ex(window, 0, idx+1, screen_size.width, screen_size.height, tcod.BKGND_SET,
                                 tcod.LEFT, line)

    #x = screen_size.width // 2 - screen_size.width // 4
    #y = screen_size.height // 2 - screen_size.height // 4
    x = screen_size.width // 10
    y = screen_size.height // 10
    tcod.console_blit(window, 0, 0, screen_size.width, screen_size.height, 0, x, y, 1.0, 0.7)

def main_menu(con, background_image, screen_size):
    tcod.image_blit_2x(background_image, 0, 0, 0)

    tcod.console_set_default_foreground(0, tcod.light_yellow)
    tcod.console_print_ex(0, int(screen_size.width / 2), int(screen_size.height / 2)- 4, tcod.BKGND_NONE, tcod.CENTER,
                          "Spellmaker")
    tcod.console_print_ex(0, int(screen_size.width / 2), int(screen_size.height / 2), tcod.BKGND_NONE, tcod.CENTER,
                          "by dutt")

    menu(con, "", ["Play a new game", "Quit"], 24, screen_size)
