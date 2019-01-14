import json

from map_related.map_util import load_map, get_monster
from graphics.assets import Assets

class MapFileLoader:

    @staticmethod
    def make_map(constants, level, file_path):
        retr = load_map(file_path + ".map", level)
        MapFileLoader.fill_in(retr, file_path + ".data")
        return retr

    @staticmethod
    def fill_in(game_map, path):
        with open(path, 'r') as reader:
            content = reader.read()
        data = json.loads(content)
        entities = []
        for m in data["monsters"]:
            entities.extend(MapFileLoader.place_monster(game_map, m))
        game_map.entities = entities


    @staticmethod
    def place_monster(game_map, monster):
        type = monster["type"]
        x = monster["x"]
        y = monster["y"]
        assets = Assets.get()
        return get_monster(x, y, game_map, room=None, monster_choice=type, assets=assets, entities=[])
