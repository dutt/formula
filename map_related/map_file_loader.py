import json

from components.drawable import Drawable
from components.stairs import Stairs
from components.entity import Entity
from graphics.assets import Assets
from graphics.render_order import RenderOrder
from map_related.map_util import load_map, get_monster


class MapFileLoader:
    @staticmethod
    def make_map(constants, level, file_path):
        retr = load_map(file_path + ".map", level)
        MapFileLoader.fill_in(retr, file_path + ".data")
        return retr

    @staticmethod
    def fill_in(game_map, path):
        with open(path, "r") as reader:
            content = reader.read()
        data = json.loads(content)
        entities = []
        for m in data["monsters"]:
            entities.extend(MapFileLoader.place_monster(game_map, m))
        if "stairs" in data:
            for s in data["stairs"]:
                entities.extend(MapFileLoader.place_stairs(game_map, s))
        game_map.entities = entities

    @staticmethod
    def place_monster(game_map, monster):
        type = monster["type"]
        x = monster["x"]
        y = monster["y"]
        assets = Assets.get()
        return get_monster(
            x, y, game_map, room=None, monster_choice=type, assets=assets, entities=[]
        )

    @staticmethod
    def place_stairs(game_map, stairs_data):
        x = stairs_data["x"]
        y = stairs_data["y"]
        stairs_component = Stairs(game_map.dungeon_level + 1)
        drawable_component = Drawable(Assets.get().stairs)
        stairs = Entity(
            x,
            y,
            "Stairs",
            render_order=RenderOrder.STAIRS,
            stairs=stairs_component,
            drawable=drawable_component,
        )
        return [stairs]
