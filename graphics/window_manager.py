from events import Event
from game_states import GameStates
from graphics.formula_window import FormulaWindow, FormulaHelpWindow
from graphics.minor_windows import WelcomeWindow, GeneralHelpWindow
from graphics.story_window import StoryWindow, StoryHelpWindow
from graphics.level_up_window import LevelUpWindow

class WindowManager:
    def __init__(self):
        self.windows = []
        self.state_wnd_mapping = {
            GameStates.WELCOME_SCREEN: WelcomeWindow,
            GameStates.STORY_SCREEN: StoryWindow,
            GameStates.STORY_HELP_SCREEN: StoryHelpWindow,
            GameStates.FORMULA_SCREEN: FormulaWindow,
            GameStates.FORMULA_HELP_SCEEN: FormulaHelpWindow,
            GameStates.GENERAL_HELP_SCREEN: GeneralHelpWindow,
            GameStates.LEVEL_UP : LevelUpWindow
        }
        self.active = []

    def push(self, window):
        self.windows.append(window)

    def pop(self):
        self.windows.pop()

    def remove(self, window):
        self.windows.remove(window)

    def handle_click(self, game_data, gfx_data, mouse_action):
        for wnd in reversed(self.windows):
            if wnd.is_clicked(mouse_action):
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

    def get_wnd_for_state(self, state):
        if state in self.state_wnd_mapping:
            return self.get(self.state_wnd_mapping[state])
        return None

    def draw(self, game_data, gfx_data):
        drawing = []
        for wnd in self.windows:
            if wnd.draw(game_data, gfx_data):
                drawing.append(wnd)
        if drawing != self.active:
            types = [type(d) for d in drawing]
            print(types)
            self.active = drawing

    def get(self, wndtype):
        for wnd in self.windows:
            if type(wnd) == wndtype:
                return wnd
        return None
