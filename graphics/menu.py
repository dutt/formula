import textwrap

import pygame

from graphics.display_helpers import display_text, display_menu, display_lines

def story_screen(gfx_data, story_data):
    surface = pygame.Surface((800, 600))
    page_lines = story_data.current_page.split("\n")
    lines = []
    for pl in page_lines:
        if pl == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(pl, 60))
    display_menu(gfx_data, lines, (800, 600), surface=surface)
    display_text(surface, "{}/{}".format(story_data.page_num, story_data.page_count),
                 gfx_data.assets.font_message, (40, 400))
    gfx_data.main.blit(surface, (200, 200))


def story_screen_help(gfx_data):
    lines = [
        "This is the next page of the story",
        "",
        "Press Space for the next page",
        "Press Escape or Tab to go back",
    ]
    display_menu(gfx_data, lines, (800, 600))


def formula_menu(gfx_data, formulabuilder):
    surface = pygame.Surface((800, 600))
    linediff = 12
    y = 5 * linediff
    display_text(surface, "Formulas", gfx_data.assets.font_message, (50, y))

    y += 2 * linediff
    display_text(surface, "Vial slots:", gfx_data.assets.font_message, (50, y))
    y += linediff
    for idx, formula in enumerate(formulabuilder.current_slots):
        text = "Slot {}: {}".format(idx, formula.name)
        if idx == formulabuilder.currslot:
            text += "<-- "
        display_text(surface, text, gfx_data.assets.font_message, (50, y))
        y += linediff

    y += 3 * linediff
    display_text(surface, "Formula {}".format(formulabuilder.currformula + 1), gfx_data.assets.font_message, (50, y))
    formulas = formulabuilder.evaluate()
    y += linediff
    display_text(surface,
                 "Formula stats:",
                 gfx_data.assets.font_message,
                 (50, y))
    y += linediff
    lines = textwrap.wrap(formulas[formulabuilder.currformula].text_stats, 60)
    display_lines(surface, gfx_data.assets.font_message, lines, 50, y, ydiff=10)
    y += len(lines) * linediff

    y += 6 * linediff
    display_text(surface, "Press Tab for help".format(formulabuilder.currformula + 1), gfx_data.assets.font_message,
                 (50, y))
    gfx_data.main.blit(surface, (200, 200))


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


def welcome_menu(gfx_data):
    lines = [
        "Welcome to Formula",
        "",
        "A game of dungeon crawling, potion brewing and vial slinging",
        "",
        "Next you'll be shown the formula screen, press Tab to show help",
        "Escape to cancel actions or quit the current menu, or the game",
        "",
        "Press Escape to continue"
    ]
    display_menu(gfx_data, lines, (800, 600))


def help_menu(gfx_data):
    lines = [
        "How to play",
        "WASD: to walk around",
        "1-5: Cast vial",
        "E: Interact",
        "You select targets using the mouse",
        "    Throw with left click, cancel with right click",
        "",
        "ESCAPE: Close current screen",
        "TAB: Show help for the current screen"
    ]
    display_menu(gfx_data, lines, (800, 600))


def formula_help_menu(gfx_data):
    lines = [
        "Building formulas:",
        "Q,W,E,R,A,S, D: Set current slot to ingredient",
        "Up/down arrow: Switch to next/previous slot",
        "Right/left arrow: Switch to next/previous formula",
        "Cooldown is increased for every used slot",
        "",
        "Adding fire to a formula increases damage",
        "Adding life to a formula increases healing",
        "Adding range to a formula makes it reach further",
        "Adding area to a formula gives it wider area of effect"
    ]
    display_menu(gfx_data, lines, (800, 600))
