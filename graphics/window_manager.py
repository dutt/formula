from components.events import EventType
from components.game_states import GameStates
from graphics.formula_window import FormulaWindow, FormulaHelpWindow
from graphics.level_up_window import LevelUpWindow
from graphics.minor_windows import (
    GeneralHelpWindow,
    AskQuitWindow,
    DeadWindow,
    VictoryWindow,
)
from graphics.setup_window import SetupWindow
from graphics.story_window import StoryWindow, StoryHelpWindow
from graphics.game_window import GameWindow
from graphics.right_panel_window import RightPanelWindow
from graphics.console_window import ConsoleWindow
from graphics.crafting_window import CraftingWindow, CraftingHelpWindow
from graphics.inventory_window import InventoryWindow, InventoryHelpWindow

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
            GameStates.PLAYER_DEAD: DeadWindow,
            GameStates.VICTORY: VictoryWindow,
            GameStates.PLAY: RightPanelWindow,
            GameStates.CONSOLE: ConsoleWindow,
            GameStates.CRAFTING : CraftingWindow,
            GameStates.CRAFTING_HELP : CraftingHelpWindow,
            GameStates.INVENTORY : InventoryWindow,
            GameStates.INVENTORY_HELP : InventoryHelpWindow,
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
            console = key_action.get(EventType.console)
            if console and game_data.state != GameStates.CONSOLE:
                console_wnd = self.get_wnd_for_state(GameStates.CONSOLE)
                console_wnd.activate(game_data, gfx_data)
                self.activate_wnd_for_state(GameStates.CONSOLE, game_data, gfx_data)
                return True, {}

            res = wnd.handle_key(game_data, gfx_data, key_action)
            if res is None:
                return False, key_action  # not handled, game can handle it

            show_window = res.get(EventType.show_window)
            if show_window:
                wnd = self.get(show_window)
                assert wnd
                game_data.prev_state.append(game_data.state)
                game_data.state = self.get_state_for_wnd(show_window)
                wnd.visible = True

            activate_wnd_for_state = res.get(EventType.activate_for_new_state)
            if activate_wnd_for_state:
                self.activate_wnd_for_state(game_data.state, game_data, gfx_data)

            message = res.get("message")
            if message:
                game_data.log.add_message(message)

            return True, {}
        return False, key_action

    def activate_wnd_for_state(self, state, game_data, gfx_data):
        wnd = self.get_wnd_for_state(state)
        assert wnd
        wnd.visible = True
        wnd.init(game_data, gfx_data)
        self.windows = sorted(self.windows, key=lambda wnd : wnd.drawing_priority, reverse=True)

    def get_state_for_wnd(self, wnd):
        for state, w in self.state_wnd_mapping.items():
            if w == wnd:
                return state

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
            show_window = res.get(EventType.show_window)
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
