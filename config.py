import argparse
import os
import sys
import json

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
ingredient_scaling_help = """Turn ingredient effectiveness scaling on?
Usage:
    --ingredient_scaling
"""
test_help = """Run an automated test
Usage:
    --test PATH_TO_FILE"""

stats_help = """Print statistics for balancing
Usage:
    ---stats
"""
profiling_help = """Save statistics from profiling
Usage:
    ---profiling
"""
ingredient_pickup_help = """Do you want to have unlimited ingredientes, or find them during the game?
Allowed choices:
    unlimited - Use however many you want
    find - Find ingredients during the game and use them
"""
ingredient_pickup_startcount_help = """How many ingredients do you want to start with?
Allowed choices:
    N - where N is an integer
    base - a basic selection
"""
ingredient_crafting_help = """Enable ingredient crafting
Usage:
    --crafting
"""
consumables_help = """ Enable consumables
Usage:
    --consumables
"""
trap_help = """Enable trap ingredient"""
trapcast_help = """Enable casting all formulas as traps"""
heal_help = """Enable life ingredient"""
formula_description = "Formula, a roguelite game about blending stuff and throwing them at monsters"

parser = argparse.ArgumentParser(description=formula_description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--unlocking", type=str, default="level_all", action="store", help=unlocking_help)
parser.add_argument("--cooldown", type=str, default="unary", action="store", help=cooldown_help)
parser.add_argument("--seed", type=str, default="now", action="store", help=seed_help)
parser.add_argument(
    "--starting_mode", type=str, default="choose", action="store", help=starting_mode_help,
)
parser.add_argument("--replay_log_path", type=str, action="store", default=replay_off, help=replay_help)
parser.add_argument("--keys", type=str, action="store", default="keys", help=keys_help)
parser.add_argument(
    "--ingredient_scaling", action="store_true", help=ingredient_scaling_help,
)
parser.add_argument("--test", type=str, action="store", default=None, help=test_help)
parser.add_argument("--stats", action="store_true", help=stats_help)
parser.add_argument("--profiling", action="store_true", help=profiling_help)
parser.add_argument("--pickup", action="store", default="find", help=ingredient_pickup_help)
parser.add_argument(
    "--pickupstartcount", action="store", default="base", help=ingredient_pickup_startcount_help,
)
parser.add_argument("--crafting", action="store_true", help=ingredient_crafting_help)
parser.add_argument("--consumables", action="store_true", help=consumables_help)
parser.add_argument("--trap", action="store_true", help=trap_help)
parser.add_argument("--trapcast", action="store_true", help=trapcast_help)
parser.add_argument("--heal", action="store_true", help=heal_help)
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

        self.replay_log_path = args.replay_log_path
        if not os.path.exists(self.replay_log_path) and self.replay_log_path != replay_off:
            print("Invalid file to reply log path: {}".format(os.path.abspath(self.replay_log_path)))
            sys.exit(1)
        self.is_replaying = self.replay_log_path != replay_off
        if self.is_replaying:
            print(f"Replaying log file {self.replay_log_path}")
        else:
            text = "Config: unlock mode {}, cooldown mode {}, seed {}, starting mode {}, keys {}"
            print(text.format(self.unlock_mode, self.cooldown_mode, self.random_seed, self.starting_mode, self.keys,))

        self.test_file = args.test
        if self.test_file:
            self.parse_test(self.test_file)
        else:
            self.is_testing = False

        self.stats = args.stats
        self.profiling = args.profiling

        self.pickup = args.pickup
        assert self.pickup in ["unlimited", "find"]
        self.pickup = self.pickup == "find"

        self.pickupstartcount = args.pickupstartcount
        if self.pickupstartcount:
            if self.pickupstartcount != "base":
                try:
                    self.pickupstartcount = int(self.pickupstartcount)
                except:
                    sys.exit(f"pickupstartcount, {self.pickupstartcount} doesn't seem to be a number")

        self.crafting = args.crafting
        self.consumables = args.consumables

        self.trap = args.trap
        self.trapcast = args.trapcast
        if self.trap and self.trapcast:
            sys.exit("Can't have both trap and trapcast enabled")

        self.heal = args.heal

    def serialize(self):
        return {
            "unlock_mode": self.unlock_mode,
            "cooldown_mode": self.cooldown_mode,
            "random_seed": self.random_seed,
            "starting_mode": self.starting_mode,
            "keys": self.keys,
            "pickup": self.pickup,
            "pickupstartcount": self.pickupstartcount,
            "crafting": self.crafting,
            "consumables": self.consumables,
            "trap": self.trap,
            "trapcast": self.trapcast,
            "heal": self.heal,
        }

    def deserialize(self, data):
        self.unlock_mode = data["unlock_mode"]
        self.cooldown_mode = data["cooldown_mode"]
        self.random_seed = data["random_seed"]
        self.starting_mode = data["starting_mode"]
        self.keys = data["keys"]
        self.pickup = data["pickup"]
        self.pickupstartcount = data["pickupstartcount"]
        self.crafting = data["crafting"]
        self.consumables = data["consumables"]
        self.trap = data["trap"]
        self.trapcast = data["trapcast"]
        self.heal = data["heal"]

    def parse_test(self, filepath):
        self.test_file = os.path.abspath(filepath)
        if not os.path.exists(self.test_file):
            raise ValueError(f"Testcase file {self.test_file} doesn't exist")
        testdir, _ = os.path.split(self.test_file)
        self.test_data = json.load(open(self.test_file, "r"))
        self.is_testing = True
        self.is_replaying = True
        self.replay_log_path = os.path.join(testdir, self.test_data["logfile"])
        if not os.path.exists(self.replay_log_path):
            raise ValueError(f"Logfile {self.replay_log_path} used in testcase {self.test_file} doesn't exist")
        self.log_data = json.load(open(self.replay_log_path, "r"))
        self.deserialize(self.log_data["config"])
        self.random_seed = self.log_data["seed"]


conf = Config()
