import textwrap
from enum import Enum, auto

import tcod

from graphics.constants import CELL_WIDTH, CELL_HEIGHT
from util import Pos, Size
from components.game_states import GameStates
import config


class MessageType(Enum):
    LINE = auto()
    BOX = auto()


class Message:
    def __init__(self, text, pos, type, size=None):
        self.text = text
        self.pos = pos
        self.type = type
        self.size = size


class Tutorial:
    TUTORIAL_SKIPPED = False

    @staticmethod
    def get_messages(game_data, gfx_data):
        messages = []

        if Tutorial.TUTORIAL_SKIPPED:
            return messages

        px, py = game_data.player.pos.tuple()
        px, py = gfx_data.camera.map_to_screen(px, py)
        px, py = px * CELL_WIDTH + 40, py * CELL_HEIGHT

        first_pos = game_data.map.orig_player_pos
        second_pos = Pos(first_pos.x + 1, first_pos.y)
        third_pos = Pos(second_pos.x + 1, second_pos.y)
        fourth_pos = Pos(third_pos.x + 1, third_pos.y)

        if len(game_data.stats.moves) == 1 and game_data.player.pos != second_pos:
            Tutorial.TUTORIAL_SKIPPED = True  # player wanted to skip tutorial
            return messages

        if not game_data.stats.moves:
            # show general help and move help
            welcome_px, welcome_py = px, py
            messages.append(Message("Welcome to formula!", Pos(welcome_px, welcome_py), MessageType.LINE))
            messages.append(
                Message(
                    "Move right for tutorial, move down to skip",
                    Pos(welcome_py + 40, welcome_py + 40),
                    MessageType.LINE,
                )
            )
            x = 20
            y = 370
            diff = 30
            messages.append(Message("Use W,A,S,D to move", Pos(x, y), MessageType.LINE))
            y += diff
            messages.append(
                Message("You can also left-click on explored tiles to move there", Pos(x, y), MessageType.LINE,)
            )
            y += diff
            messages.append(Message("Press Tab for help", Pos(x, y), MessageType.LINE))
            y += diff
            messages.append(Message("Press Escape to quit", Pos(x, y), MessageType.LINE))
            #messages.append(Message("Press Alt-Enter for fullscreen", Pos(20, 460), MessageType.LINE))
            # text = "These are your formulas. You will gain more formulas, slots and ingredients as you level up"
            # messages.append(Message(text, Pos(20, 200), MessageType.LINE, Size(200, 150)))

            # pygame.draw.rect(help_surface, colors.BACKGROUND, pygame.rect.Rect(20, 200, 200, 150))

            # lines = textwrap.wrap(text, 20)
            # display_lines(help_surface, assets.font_message, lines, 25, 205)

            # move_px, move_py = px, py + 40
            # messages.append(Message("Use W,A,S,D to move", Pos(move_px, move_py), MessageType.LINE))

        elif game_data.player.pos == second_pos:
            messages.append(Message("<--- This is your health bar", Pos(0, 20), MessageType.LINE))
            messages.append(Message("<--- This is your shield bar", Pos(0, 70), MessageType.LINE))
            if not config.conf.keys:
                messages.append(Message("This is your experience bar", Pos(20, 140), MessageType.LINE))
            else:
                messages.append(
                    Message(
                        "On each level there's a number of keys. Find them all to unlock the stairs",
                        Pos(20, 110),
                        MessageType.LINE,
                    )
                )

        elif game_data.player.pos == third_pos:
            cast_px, cast_py = px, py + 40
            messages.append(Message("Press 1,2 or 3 to select vial", Pos(cast_px, cast_py), MessageType.LINE,))
            messages.append(
                Message("FFR is Fire, Fire, Range. Short range, high damage", Pos(20, 220), MessageType.LINE,)
            )
            messages.append(
                Message("FRR is Fire, Range, Range. Longer range, lower damage", Pos(20, 260), MessageType.LINE,)
            )
            messages.append(
                Message(
                    "This is a shield, activate it and it will protect you from damage", Pos(20, 300), MessageType.LINE,
                )
            )

        elif game_data.player.pos == fourth_pos:
            messages.append(Message("This first enemy is inactive, others won't be.", Pos(80, 160), MessageType.LINE,))
            messages.append(
                Message("Kill it the second Formula, FRR", Pos(80, 200), MessageType.LINE,)
            )
            messages.append(Message("Press 2, or click the formula, to target", Pos(80, 240), MessageType.LINE,))

            messages.append(Message("Defensive formulas will always target yourself", Pos(80, 300), MessageType.LINE,))

        elif game_data.player.pos == Pos(14,5):
            x = 20
            y = 200
            diff = 30
            messages.append(Message("This is a key, you need these to unlock stairs", Pos(x, y), MessageType.LINE))
            messages.append(Message("Move onto it and press space to pick it up", Pos(x, y + diff), MessageType.LINE))
            messages.append(Message("When you do, you'll get a little loot", Pos(x, y + 2*diff), MessageType.LINE))

        elif game_data.player.pos == Pos(10,5):
            for e in game_data.map.entities:
                if e.stairs and tcod.map_is_in_fov(game_data.fov_map, e.pos.x, e.pos.y):
                    sx, sy = gfx_data.camera.map_to_screen(e.pos.x, e.pos.y)
                    sx, sy = sx, sy * CELL_HEIGHT + CELL_HEIGHT
                    messages.append(Message("Stairs, press Space to ascend", Pos(sx, sy), MessageType.LINE))
                    break

        else:
            has_killed = game_data.stats.monsters_killed_level == 1
            has_not_looted = game_data.stats.num_looted_monsters == 0 and not config.conf.keys
            has_cooldown = game_data.player.caster.has_cooldown()
            if has_killed and (has_not_looted or has_cooldown):
                monster = game_data.stats.monsters_killed_per_level[0][0]
                mx, my = gfx_data.camera.map_to_screen(monster.pos.x, monster.pos.y)
                mx, my = mx * CELL_WIDTH + 40, my * CELL_HEIGHT
                if not config.conf.keys:
                    messages.append(Message("Go to the corpse and press space to loot", Pos(mx, my), MessageType.LINE,))
                messages.append(Message("Now your formula is on cooldown", Pos(20, 220), MessageType.LINE))
                messages.append(Message("Cooldown reduce when you explore new tiles", Pos(20, 260), MessageType.LINE,))

        if game_data.state == GameStates.TARGETING:
            target_px, target_py = px, py + 40
            messages.append(Message("Left click target to throw vial", Pos(target_px, target_py), MessageType.LINE,))

        return messages
