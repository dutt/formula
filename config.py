import argparse

unlocking_help="""Are ingredients unlocked?
Allowed choices: 
  none - no unlocking, start with all ingredients
  level - unlock ingredient on level up"""
cooldown_help="""How does cooldown work?
Allowed choices:
 always - always tick cooldowns 1 per round
 unary - tick 1 cooldown if you explore new tiles
 counting - tick 1 cooldown per newly explored tile"""
seed_help="Random seed, defaults to current timestamp. Can be any value"
starting_mode_help="""What formulas do you start with?
Allowed choices:
 choose - start with showing the formula screen
 fire - FFF, FFR, FFR
"""
formula_description="Formula, a roguelite game about blending stuff and throwing them at monsters"
parser = argparse.ArgumentParser(description=formula_description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--unlocking", type=str, default="none", action="store", help=unlocking_help)
parser.add_argument("--cooldown", type=str, default="always", action="store", help=cooldown_help)
parser.add_argument("--seed", type=str, default="now", action="store", help=seed_help)
parser.add_argument("--starting_mode", type=str, default="fire", action="store", help=starting_mode_help)
args = parser.parse_args()


class Config:
    def __init__(self):
        print(args)
        self.unlock_mode = args.unlocking
        assert self.unlock_mode in ["none", "level"]
        self.cooldown_mode = args.cooldown
        assert self.cooldown_mode in ["always", "unary", "counting"]
        self.random_seed = args.seed
        self.starting_mode = args.starting_mode
        assert self.starting_mode in ["choose", "fire"]


conf = Config()
