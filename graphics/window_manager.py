from events import Event
from game_states import GameStates
from graphics.formula_window import FormulaWindow, FormulaHelpWindow
from graphics.level_up_window import LevelUpWindow
from graphics.minor_windows import GeneralHelpWindow, AskQuitWindow
from graphics.setup_window import SetupWindow
from graphics.story_window import StoryWindow, StoryHelpWindow


class WindowManager:
    def __init__(self):
        self.windows = []
        self.state_wnd_mapping = {
            GameStates.SETUP: SetupWindow,
            GameStates.STORY_SCREEN: StoryWindow,
            GameStates.STORY_HELP_SCREEN: StoryHelpWindow,
            GameStates.FORMULA_SCREEN: FormulaWindow,
            GameStates.FORMULA_HELP_SCEEN: FormulaHelpWindow,
            GameStates.GENERAL_HELP_SCREEN: GeneralHelpWindow,
            GameStates.LEVEL_UP: LevelUpWindow,
            GameStates.ASK_QUIT: AskQuitWindow,
            GameStates.PLAYER_DEAD: AskQuitWindow,
        }

    def push(self, window):
        self.windows.append(window)

    def pop(self):
        self.windows.pop()

    def remove(self, window):
        self.windows.remove(window)

    def handle_click(self, game_data, gfx_data, mouse_action):
        for wnd in reversed(self.windows):
            if wnd.visible and wnd.is_clicked(mouse_action):
                return wnd.handle_click(game_data, gfx_data, mouse_action)
        return {}

    def handle_key(self, game_data, gfx_data, key_action):
        wnd = self.get_wnd_for_state(game_data.state)
        if wnd:
            res = wnd.handle_key(game_data, gfx_data, key_action)
            if res is None:
                return False, key_action  # not handled, game can handle it
            show_window = res.get(Event.show_window)
            if show_window:
                wnd = self.get(show_window)
                if wnd:
                    wnd.visible = True
            return True, {}
        return False, key_action

    def activate_wnd_for_state(self, state):
        wnd = self.get_wnd_for_state(state)
        assert wnd
        wnd.visible = True

    def get_wnd_for_state(self, state):
        if state in self.state_wnd_mapping:
            return self.get(self.state_wnd_mapping[state])
        return None

    def draw(self, game_data, gfx_data):
        def helper(wnd):
            if not wnd.visible:
                return
            res = wnd.draw(game_data, gfx_data)
            if not res:
                return
            show_window = res.get(Event.show_window)
            if not show_window:
                return
            wnd = self.get(show_window)
            if wnd:
                wnd.visible = True

        for wnd in self.windows:
            helper(wnd)
            for child in wnd.children:
                helper(child)

    def get(self, wndtype):
        for wnd in self.windows:
            if type(wnd) == wndtype:
                return wnd
        return None
