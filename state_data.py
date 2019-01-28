from statistics import Statistics


class StateData():
    def __init__(self, player, log, constants, timesystem,
                 fov_map, fov_recompute, story_data, run_planner, formula_builder, menu_data,
                 state):
        self.player = player
        self.log = log
        self.constants = constants
        self.timesystem = timesystem
        self.fov_map = fov_map
        self.fov_recompute = fov_recompute
        self.story = story_data
        self.run_planner = run_planner
        self.formula_builder = formula_builder
        self.targeting_formula = None,
        self.menu_data = menu_data
        self.state = state
        self.prev_state = []
        self.stats = Statistics()
