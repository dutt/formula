from enum import Enum, auto


class GameStates(Enum):
    SETUP = auto()
    WELCOME_SCREEN = auto()
    GENERAL_HELP_SCREEN = auto()
    PLAY = auto()
    PLAYER_DEAD = auto()
    TARGETING = auto()
    LEVEL_UP = auto()
    CHARACTER_SCREEN = auto()
    FORMULA_SCREEN = auto()
    FORMULA_HELP_SCEEN = auto()
    STORY_SCREEN = auto()
    STORY_HELP_SCREEN = auto()
    VICTORY = auto()
    ASK_QUIT = auto()
    CONSOLE = auto()
    CRAFTING = auto()
