import argparse
import os
import sys

unlocking_help = """Are ingredients unlocked?
Allowed choices: 
  none - no unlocking, start with all ingredients
  level_2random - unlock ingredient on level up, choose between 2 random on level up
  level_all - unlock ingredients on level up, choose between all"""
cooldown_help = """How does cooldown work?
Allowed choices:
 always - always tick cooldowns 1 per round
 unary - tick 1 cooldown if you explore new tiles
 counting - tick 1 cooldown per newly explored tile"""
seed_help = "Random seed, defaults to current timestamp. Can be any value"
starting_mode_help = """What formulas do you start with?
Allowed choices:
 choose - start with showing the formula screen
 fire - FFR, FFR, FFR
"""
replay_help = """Replay a game log, log values override all other settings. 
Argument is the path to the log file
"""
replay_off = "off"
keys_help = """Do you want to kill monsters or collect keys?
Allowed choices:
   kill - XP for killing monsters, no keys
   keys - XP per level
"""
ingredient_scaling_help = """Should ingredient effectiveness scale?
Allowed choices:
   yes - Ingredients become less effective the more you have
   no - Ingredients don't become less effective
"""
formula_description = (
    "Formula, a roguelite game about blending stuff and throwing them at monsters"
)

parser = argparse.ArgumentParser(
    description=formula_description, formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "--unlocking", type=str, default="level_all", action="store", help=unlocking_help
)
parser.add_argument(
    "--cooldown", type=str, default="unary", action="store", help=cooldown_help
)
parser.add_argument("--seed", type=str, default="now", action="store", help=seed_help)
parser.add_argument(
    "--starting_mode", type=str, default="fire", action="store", help=starting_mode_help
)
parser.add_argument(
    "--replay_log_path", type=str, action="store", default=replay_off, help=replay_help
)
parser.add_argument("--keys", type=str, action="store", default="kill", help=keys_help)
parser.add_argument(
    "--ingredient_scaling",
    type=str,
    action="store",
    default="no",
    help=ingredient_scaling_help,
)
args = parser.parse_args()


class Config:
    def __init__(self):
        self.random_seed = args.seed

        self.unlock_mode = args.unlocking
        assert self.unlock_mode in ["none", "level_2random", "level_all"]

        self.cooldown_mode = args.cooldown
        assert self.cooldown_mode in ["always", "unary", "counting"]

        self.starting_mode = args.starting_mode
        assert self.starting_mode in ["choose", "fire"]

        self.keys = args.keys
        assert self.keys in ["kill", "keys"]
        self.keys = self.keys == "keys"

        self.ingredient_scaling = args.ingredient_scaling
        assert self.ingredient_scaling in ["yes", "no"]
        self.ingredient_scaling = self.ingredient_scaling == "yes"

        self.replay_log_path = args.replay_log_path
        if (
            not os.path.exists(self.replay_log_path)
            and self.replay_log_path != replay_off
        ):
            print(
                "Invalid file to reply log path: {}".format(
                    os.path.abspath(self.replay_log_path)
                )
            )
            sys.exit(1)
        self.is_replaying = self.replay_log_path != replay_off
        if self.is_replaying:
            text = "Replaying log file {}".format(self.replay_log_path)
        else:
            text = "Config: unlock mode {}, cooldown mode {}, seed {}, starting mode {}, keys {}"

        print(
            text.format(
                self.unlock_mode,
                self.cooldown_mode,
                self.random_seed,
                self.starting_mode,
                self.keys,
            )
        )


conf = Config()
