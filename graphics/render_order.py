from enum import Enum, auto


class RenderOrder(Enum):
    DECOR = auto()
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
