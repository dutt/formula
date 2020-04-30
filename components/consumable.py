from graphics.assets import Assets

def get_tiles_within(map, distance, target):
    import math

    from util import Pos

    retr = []
    for x in range(
                math.ceil(target.x - distance),
                math.ceil(target.x + distance),
            ):
                for y in range(
                    math.ceil(target.y - distance),
                    math.ceil(target.y + distance),
                ):
                    dist = math.sqrt((x - target.x) ** 2 + (y - target.y) ** 2)
                    if dist < distance:
                        retr.append(Pos(x, y))
    return retr

class Consumable():
    def __init__(self, name, targeted, distance=1, area=1):
        self.name = name
        self.distance = distance
        self.targeted = targeted
        self.area = area

    def apply(self, game_data, target):
        raise NotImplementedError("apply() called on Consumable baseclass")

class Firebomb(Consumable):
    DESCRIPTION="""
        Firebomb, throw to deal high aoe damage
    """

    def __init__(self):
        super().__init__(name="Firebomb", targeted=True, distance=5, area=2)

    def apply(self, game_data, gfx_data, target):
        # create graphcs
        tile_pos = get_tiles_within(game_data.map, self.area, target)
        for pos in tile_pos:
            gfx_data.visuals.add_temporary(pos, pos, lifespan=0.2, asset=Assets.get().spark_effect, wait=0.2)

class Freezebomb(Consumable):
    DESCRIPTION="""
        Freezebomb, throw to stun
    """

    def __init__(self):
        super().__init__(name="Freezebomb", targeted=True, distance=5, area=2)

    def apply(self, game_data, gfx_data, target):
        # create graphcs
        tile_pos = get_tiles_within(game_data.map, self.area, target)
        for pos in tile_pos:
            gfx_data.visuals.add_temporary(pos, pos, lifespan=0.2, asset=Assets.get().spark_effect, wait=0.2)

class Teleporter(Consumable):
    DESCRIPTION="""
        Teleporter, teleport to a visited location
    """

    def __init__(self):
        super().__init__(name="Teleporter", targeted=False)

    def apply(self, game_data, gfx_data, target):
        print(f"applying Teleporter at {target}")

class CooldownClear(Consumable):
    DESCRIPTION="""
        CooldownClear
    """

    def __init__(self):
        super().__init__(name="CooldownClear", targeted=False)

    def apply(self, game_data, gfx_data, target):
        print(f"applying CooldownClear at {target}")

class Thingy(Consumable):
    DESCRIPTION="""
        Thingy
    """

    def __init__(self):
        super().__init__(name="Thingy", targeted=False)

    def apply(self, game_data, gfx_data, target):
        print(f"applying Thingy at {target}")

class Thingmajig(Consumable):
    DESCRIPTION="""
        Thingmajig
    """

    def __init__(self):
        super().__init__(name="Thingmajig", targeted=False)

    def apply(self, game_data, gfx_data, target):
        print(f"applying Thingmajig at {target}")
