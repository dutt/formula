import math
import os
import sys


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<size w={}, h={}>".format(self.width, self.height)

    def tuple(self):
        return (self.width, self.height)


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return (self == other) == False

    def __str__(self):
        return "<Pos x={} y={}>".format(self.x, self.y)

    def __repr__(self):
        return str(self)

    def tuple(self):
        return self.x, self.y


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
