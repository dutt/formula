from graphics.story_window import StoryWindow
from graphics.window import TextWindow


class WelcomeWindow(TextWindow):
    LINES = [
        "Welcome to Formula",
        "",
        "A game of dungeon crawling, potion brewing and vial slinging",
        "",
        "Next you'll be shown the formula screen, press Tab to show help",
        "Escape to cancel actions or quit the current menu, or the game",
        "",
        "Press Escape to continue"
    ]

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, WelcomeWindow.LINES, StoryWindow)


class GeneralHelpWindow(TextWindow):
    LINES = [
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

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, GeneralHelpWindow.LINES, None)
