import pygame

from graphics.display_helpers import display_text
from graphics.window import Window
from components.events import EventType
from components.game_states import GameStates
from systems.console import Console
from util import Size, Pos

class ConsoleWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(Pos(0, 0), Size(constants.window_size.width, constants.window_size.height * 0.5), visible=visible)
        self.line = ""
        self.linepos = (20, self.size.height - 30)
        self.history = []
        self.history_linecount = (self.size.height - 20) / 15

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())
        surface.fill((50, 30, 30))

        ypos = 15
        if len(self.history) > self.history_linecount:
            historylines = self.history[-self.history_linecount:]
        else:
            historylines = self.history
        for line in historylines:
            display_text(surface, line, gfx_data.assets.font_console, (10, ypos))
            ypos += 20

        display_text(surface, self.line, gfx_data.assets.font_console, self.linepos)

        line_y = self.linepos[1] - 5
        pygame.draw.line(surface, (200, 200, 200), (0, line_y), (self.size.width, line_y))

        gfx_data.main.blit(surface, self.pos.tuple())

    def apply(self, game_data):
        print(f"Running command <{self.line}>")
        self.history.append(self.line)
        self.history.extend(Console.execute(self.line, game_data))
        self.line = ""

    def handle_key(self, game_data, gfx_data, key_action):
        console = key_action.get(EventType.console)
        if console:
            return self.close(game_data, activate_for_new_state=True)

        key = key_action.get("key")
        if key:
            self.line += chr(key)

        apply = key_action.get("apply")
        if apply:
            self.apply(game_data)

        backspace = key_action.get("backspace")
        if backspace:
            self.line = self.line[:-1]

    def activate(self, game_data, gfx_data):
        game_data.prev_state.append(game_data.state)
        game_data.state = GameStates.CONSOLE
