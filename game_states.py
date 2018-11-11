from enum import Enum, auto


class GameStates(Enum):
    PLAY = auto()
    PLAYER_DEAD = auto()
    TARGETING = auto()
    LEVEL_UP = auto()
    CHARACTER_SCREEN = auto()
    SPELLMAKER_SCREEN = auto()
    SPELLMAKER_HELP_SCEEN = auto()
    GENERAL_HELP_SCREEN = auto()
    WELCOME_SCREEN = auto()
