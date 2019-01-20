import argparse

unlocking_help="""Allowed choices: 
  none - no unlocking, start with all ingredients
  level - unlock ingredient on level up"""
cooldown_help="""Allowed choices:
 always - always tick cooldowns 1 per round
 unary - tick 1 cooldown if you explore new tiles
 counting - tick 1 cooldown per newly explored tile"""
seed_help="Random seed, defaults to current timestamp. Can be any value"
parser = argparse.ArgumentParser(description="Formula, a roguelite game about blending stuff and throwing them at monsters",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--unlocking", type=str, default="none", action="store", help=unlocking_help)
parser.add_argument("--cooldown", type=str, default="always", action="store", help=cooldown_help)
parser.add_argument("--seed", type=str, default="now", action="store", help=seed_help)
args = parser.parse_args()


class Config:
    def __init__(self):
        print(args)
        self.unlock_mode = args.unlocking
        assert self.unlock_mode in ["none", "level"]
        self.cooldown_mode = args.cooldown
        assert self.cooldown_mode in ["always", "unary", "counting"]
        self.random_seed = args.seed


conf = Config()
