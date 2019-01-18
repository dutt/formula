import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--unlocking", type=str, default="none", action="store")
parser.add_argument("--cooldown", type=str, default="always", action="store")
args = parser.parse_args()


class Config:
    def __init__(self):
        print(args)
        self.unlock_mode = args.unlocking
        assert self.unlock_mode in ["none", "level"]
        self.cooldown_mode = args.cooldown
        assert self.cooldown_mode in ["always", "unary", "counting"]


conf = Config()
