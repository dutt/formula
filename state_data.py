class StateData():
    def __init__(self, player, entities, game_map, log, constants, timesystem,
                 fov_map, fov_recompute, story_data):
        self.player = player
        self.entities = entities
        self.map = game_map
        self.log = log
        self.constants = constants
        self.timesystem = timesystem
        self.fov_map = fov_map
        self.fov_recompute = fov_recompute
        self.story = story_data
