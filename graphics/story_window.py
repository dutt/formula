import textwrap

from graphics.display_helpers import display_menu, display_text
from graphics.game_window import GameWindow
from graphics.window import Window, TextWindow
from systems.input_handlers import EventType
from graphics.assets import Assets


class StoryHelpWindow(TextWindow):
    LINES = [
        "This is the next page of the story",
        "",
        "Use W, S or the mouse scroll to read more",
        "Press Escape to close",
        "Press Tab to return to the story from this page",
    ]

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, StoryHelpWindow.LINES, None)


class StoryWindow(Window):
    def __init__(self, constants, story_data, visible=False):
        super().__init__(
            constants.helper_window_pos, constants.helper_window_size, visible
        )
        self.story_data = story_data
        self.current_content = None
        self.current_lines = None
        self.offset = 0
        self.num_lines = 20
        self.offset_jump = 1

    def draw(self, game_data, gfx_data):

        if (
            not self.current_lines
            or self.current_content != self.story_data.current_content
        ):
            self.current_content = self.story_data.current_content
            long_lines = self.story_data.current_content.split("\n")
            lines = []
            for current in long_lines:
                if current.strip() == "":
                    lines.append(current)
                else:
                    split_lines = textwrap.wrap(current, 60)
                    lines.extend(split_lines)
            self.current_lines = lines

        show_lines = self.current_lines[self.offset : self.offset + self.num_lines]
        display_menu(gfx_data, show_lines, self.size.tuple(), x=20, starty=20)

        display_text(
            gfx_data.main,
            "Press Space to continue",
            Assets.get().font_message,
            (350, 750),
        )

    def scroll_up(self):
        if self.num_lines > len(self.current_lines):
            self.offset = max(self.offset - self.offset_jump, 0)
        else:
            self.offset = max(
                -len(self.current_lines) + self.num_lines,
                self.offset - self.offset_jump,
                0,
            )

    def scroll_down(self):
        if self.num_lines > len(self.current_lines):
            self.offset = min(self.offset + self.offset_jump, len(self.current_lines))
        else:
            self.offset = min(
                len(self.current_lines) - self.num_lines, self.offset + self.offset_jump
            )

    def handle_key(self, game_data, gfx_data, key_action):
        do_quit = key_action.get(EventType.exit)
        if do_quit:
            return self.close(game_data, GameWindow)

        next = key_action.get("next")
        if next:
            return self.close(game_data, GameWindow)

        scroll_up = key_action.get(EventType.scroll_up)
        if scroll_up:
            self.scroll_up()

        scroll_down = key_action.get(EventType.scroll_down)
        if scroll_down:
            self.scroll_down()

    def handle_click(self, game_data, gfx_data, mouse_action):
        scroll_up = mouse_action.get(EventType.scroll_up)
        if scroll_up:
            self.scroll_up()

        scroll_down = mouse_action.get(EventType.scroll_down)
        if scroll_down:
            self.scroll_down()
