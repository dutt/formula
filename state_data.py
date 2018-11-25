class StateData():
    def __init__(self, player, entities, log, constants, timesystem,
                 fov_map, fov_recompute, story_data, run_planner):
        self.player = player
        self.entities = entities
        self.log = log
        self.constants = constants
        self.timesystem = timesystem
        self.fov_map = fov_map
        self.fov_recompute = fov_recompute
        self.story = story_data
        self.run_planner = run_planner
        self.map = run_planner.current_map
