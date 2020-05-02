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

        linediff = 30

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
            messages.append(Message("Use W,A,S,D to move", Pos(x, y), MessageType.LINE))
            messages.append(
                Message("You can also left-click on explored tiles to move there", Pos(x, y+linediff), MessageType.LINE,)
            )
            messages.append(Message("Press Tab for help", Pos(x, y+linediff*2), MessageType.LINE))
            messages.append(Message("Press Escape to quit", Pos(x, y+linediff*3), MessageType.LINE))
            if config.conf.crafting:
                messages.append(Message("V to open crafting", Pos(x, y+linediff*4), MessageType.LINE))
            if config.conf.consumables:
                messages.append(Message("I to open invetory", Pos(x, y+linediff*5), MessageType.LINE))


        elif game_data.player.pos == second_pos:
            messages.append(Message("<--- This is your health bar", Pos(0, 20), MessageType.LINE))
            messages.append(Message("<--- This is your shield bar, your shield will reset after this level", Pos(0, 70), MessageType.LINE))
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
            if config.conf.consumables:
                y = 600
                messages.append(Message("Down to the left are consumables, single use items that can help", Pos(0, y), MessageType.LINE))
                messages.append(Message("You can mouse over for more info", Pos(20, y + linediff), MessageType.LINE))

        elif game_data.player.pos == third_pos:
            x = 20
            cast_px, cast_py = px, py + 40
            messages.append(Message("Press 1,2 or 3 to select vial", Pos(cast_px, cast_py), MessageType.LINE,))
            messages.append(
                Message("FFR is Fire, Fire, Range. Short range, high damage", Pos(x, 220), MessageType.LINE,)
            )
            messages.append(
                Message("FRR is Fire, Range, Range. Longer range, lower damage", Pos(x, 260), MessageType.LINE,)
            )
            messages.append(
                Message(
                    "This is a shield, activate it and it will protect you from damage", Pos(x, 300), MessageType.LINE,
                )
            )
            messages.append(
                Message(
                    "You can also melee attack enemies by moving into them, this won't deal much damage though", Pos(x, 360), MessageType.LINE,
                )
            )

        elif game_data.player.pos == fourth_pos:
            x = 80
            y = 160

            messages.append(Message("This first enemy is inactive, others won't be.", Pos(x, y), MessageType.LINE,))
            messages.append(
                Message("Kill it the second Formula, FRR", Pos(x, y + linediff), MessageType.LINE,)
            )
            messages.append(Message("Press 2, or click the formula, to target", Pos(x, y + linediff*2), MessageType.LINE,))

            messages.append(Message("Defensive formulas will always target yourself", Pos(x, y + linediff*3), MessageType.LINE,))

        elif game_data.player.pos == Pos(14,5):
            x = 20
            y = 200

            messages.append(Message("This is a key, you need these to unlock stairs", Pos(x, y), MessageType.LINE))
            messages.append(Message("Move onto it and press space to pick it up", Pos(x, y + linediff), MessageType.LINE))
            messages.append(Message("When you do, you'll get a little loot", Pos(x, y + linediff*2), MessageType.LINE))

        elif game_data.player.pos == Pos(10,5):
            for e in game_data.map.entities:
                if e.stairs and tcod.map_is_in_fov(game_data.fov_map, e.pos.x, e.pos.y):
                    sx, sy = gfx_data.camera.map_to_screen(e.pos.x, e.pos.y)
                    sx, sy = sx, sy * CELL_HEIGHT + CELL_HEIGHT
                    messages.append(Message("Stairs, press Space to ascend", Pos(sx, sy), MessageType.LINE))

                    messages.append(Message("When you ascend:", Pos(sx, sy+50), MessageType.LINE))
                    sy += 75
                    messages.append(Message("1) You will get to change your formulas", Pos(sx+30, sy), MessageType.LINE))
                    messages.append(Message("2) Your cooldowns will reset", Pos(sx+30, sy+linediff), MessageType.LINE))
                    messages.append(Message("3) Your shield will remain", Pos(sx+30, sy+linediff*2), MessageType.LINE))
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
                messages.append(Message("Cooldown reduce when you explore new tiles", Pos(20, 220+linediff), MessageType.LINE,))

        if game_data.state == GameStates.TARGETING:
            target_px, target_py = px, py + 40
            messages.append(Message("Left click target to throw vial", Pos(target_px, target_py), MessageType.LINE,))

        return messages
