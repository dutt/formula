from enum import Enum, auto


class GameState(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    PLAYER_DEAD = auto()
    SHOW_INVENTORY = auto()
    DROP_INVENTORY = auto()
    TARGETING = auto()
    LEVEL_UP = auto()
    CHARACTER_SCREEN = auto()
    SPELLMAKER_SCREEN = auto()
    SHOW_HELP = auto()
    WELCOME_SCREEN = auto()
