from systems.statistics import Statistics


class StateData:
    def __init__(
        self,
        player,
        log,
        constants,
        timesystem,
        fov_map,
        fov_recompute,
        story_data,
        run_planner,
        formula_builder,
        menu_data,
        ingredient_storage,
        inventory,
        initial_state,
        initial_state_history=[],
    ):
        self.player = player
        self.log = log
        self.constants = constants
        self.timesystem = timesystem
        self.fov_map = fov_map
        self.fov_recompute = fov_recompute
        self.story = story_data
        self.run_planner = run_planner
        self.formula_builder = formula_builder
        self.targeting_formula = (None,)
        self.targeting_formula_idx = (None,)
        self.menu_data = menu_data
        self.ingredient_storage = ingredient_storage
        self._state = initial_state
        self.prev_state = initial_state_history
        self.inventory = inventory
        self.stats = Statistics()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        print(f"setting state {new_state}, prev_state {self.prev_state}")
        self._state = new_state
