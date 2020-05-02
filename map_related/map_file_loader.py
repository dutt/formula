import json

from components.drawable import Drawable
from components.stairs import Stairs
from components.entity import Entity
from components.key import Key
from graphics.assets import Assets
from graphics.render_order import RenderOrder
from map_related.map_util import load_map
from systems.monster_generator import get_monster
from util import Pos


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

        entities.extend(MapFileLoader.load_monsters(data, game_map))
        entities.extend(MapFileLoader.load_stairs(data, game_map))
        entities.extend(MapFileLoader.load_keys(data, game_map))

        MapFileLoader.load_player(data, game_map)  # just the position

        game_map.entities = entities

    @staticmethod
    def load_monsters(data, game_map):
        retr = []
        for m in data["monsters"]:
            retr.extend(MapFileLoader.place_monster(game_map, m))
        return retr

    @staticmethod
    def load_stairs(data, game_map):
        retr = []
        for s in data["stairs"]:
            retr.extend(MapFileLoader.place_stairs(game_map, s))
        return retr

    @staticmethod
    def load_player(data, game_map):
        p = data["player"]
        game_map.player_pos = Pos(p["x"], p["y"])
        game_map.orig_player_pos = Pos(p["x"], p["y"])

    @staticmethod
    def load_keys(data, game_map):
        retr = []
        assets = Assets.get()
        for key_data in data["keys"]:
            drawable_component = Drawable(assets.key)
            key = Entity(
                key_data["x"],
                key_data["y"],
                "Key",
                render_order=RenderOrder.ITEM,
                key=Key(),
                drawable=drawable_component,
            )
            retr.append(key)
        game_map.num_keys_total = len(retr)
        return retr

    @staticmethod
    def place_monster(game_map, monster):
        type = monster["type"]
        x = monster["x"]
        y = monster["y"]
        return get_monster(x, y, game_map, room=None, monster_choice=type, entities=[])

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
