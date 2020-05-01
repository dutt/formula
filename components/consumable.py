import random

from util import Pos
from systems.effect_builder import EffectBuilder

from components.effect_type import EffectType
from components.damage_type import DamageType
from systems.messages import Message

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
    """.strip()
    DAMAGE = 5

    def __init__(self):
        super().__init__(name="Firebomb", targeted=True, distance=5, area=2)

    def apply(self, game_data, gfx_data, target):
        results = []

        # create graphcs
        target_tiles = get_tiles_within(game_data.map, self.area, target)
        for pos in target_tiles:
            gfx_data.visuals.add_temporary(pos, pos, lifespan=0.2, asset=Assets.get().spark_effect, wait=0.2)
        # cause effect
        targets = []
        for e in game_data.map.entities:
            if e.fighter and e.pos in target_tiles:
                targets.append(e)

        effect = EffectBuilder.create(EffectType.DAMAGE, amount=Firebomb.DAMAGE, dmg_type=DamageType.FIRE, rounds=1, caster=game_data.player)
        for t in targets:
            results.append({"message" : Message(f"Hit {t.name.lower()} with firebomb for {Firebomb.DAMAGE} fire damage")})
            results.extend(effect.apply(t))
        return results

class Freezebomb(Consumable):
    DESCRIPTION="""
        Freezebomb, throw to stun
    """.strip()
    DAMAGE=3
    ROUNDS = 5

    def __init__(self):
        super().__init__(name="Freezebomb", targeted=True, distance=5, area=2)

    def apply(self, game_data, gfx_data, target):
        results = []

        # create graphcs
        target_tiles = get_tiles_within(game_data.map, self.area, target)
        for pos in target_tiles:
            gfx_data.visuals.add_temporary(pos, pos, lifespan=0.2, asset=Assets.get().spark_effect, wait=0.2)
        # cause effect
        targets = []
        for e in game_data.map.entities:
            if e.fighter and e.pos in target_tiles:
                targets.append(e)

        effect = EffectBuilder.create(EffectType.DAMAGE, amount=Freezebomb.DAMAGE, dmg_type=DamageType.COLD, rounds=Freezebomb.ROUNDS, caster=game_data.player)
        for t in targets:
            results.append({"message" : Message(f"Hit {t.name.lower()} with freezebomb, slowed for {Freezebomb.ROUNDS} rounds")})
            results.extend(effect.apply(t))
        return results

class Teleporter(Consumable):
    DESCRIPTION="""
        Teleporter, teleport to a visited location
    """.strip()

    def __init__(self):
        super().__init__(name="Teleporter", targeted=False)

    def apply(self, game_data, gfx_data, target):
        explored_tiles = []
        for x in range(game_data.map.width):
            for y in range(game_data.map.height):
                if game_data.map.tiles[x][y].explored and not game_data.map.tiles[x][y].blocked:
                    explored_tiles.append((x,y))

        x, y = random.choice(explored_tiles)
        game_data.player.pos = Pos(x,y)
        results = [
            {"message" : Message("Teleported to a previously explored location")}
        ]
        return results

class CooldownClear(Consumable):
    DESCRIPTION="""
        CooldownClear
    """.strip()

    def __init__(self):
        super().__init__(name="CooldownClear", targeted=False)

    def apply(self, game_data, gfx_data, target):
        game_data.player.caster.clear_cooldowns()
        results = [
            {"message" : Message("Your cooldowns have been cleared, have at'em!")}
        ]
        return results

class Thingy(Consumable):
    DESCRIPTION="""
        Thingy
    """.strip()

    def __init__(self):
        super().__init__(name="Thingy", targeted=False)

    def apply(self, game_data, gfx_data, target):
        print(f"applying Thingy at {target}")

class Thingmajig(Consumable):
    DESCRIPTION="""
        Thingmajig
    """.strip()

    def __init__(self):
        super().__init__(name="Thingmajig", targeted=False)

    def apply(self, game_data, gfx_data, target):
        print(f"applying Thingmajig at {target}")
