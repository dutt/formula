from graphics.story_window import StoryWindow
from graphics.window import TextWindow


class WelcomeWindow(TextWindow):
    LINES = [
        "Welcome to Formula",
        "",
        "A game of dungeon crawling, potion brewing and vial slinging",
        "",
        "Press Tab to show or hide help for the current screen",
        "Space moves you to the next window",
        "Escape to cancel actions, close the current menu, or exit the game",
        "",
        "Press Space to continue",
    ]

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, WelcomeWindow.LINES, StoryWindow)


class GeneralHelpWindow(TextWindow):
    LINES = [
        "How to play:",
        "WASD: Move",
        "Number keys, 1,2,3...: Throw that vial",
        "You select targets using the mouse",
        "    Throw with left click, cancel with right click",
        "",
        "ESCAPE: Close current screen, or quit the game",
        "Space: Interact or next screen",
        "TAB: Show help for the current screen"
    ]

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, GeneralHelpWindow.LINES, None)
