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
        return self.width, self.height


class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def normalize(self):
        length = self.length()
        return Vec(self.x / length, self.y / length)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __mul__(self, other):
        if type(other) == Vec:
            return Vec(self.x * other.x, self.y * other.y)
        else:
            return Vec(self.x * other, self.y * other)

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def to_pos(self):
        return Pos(self.x, self.y)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<vec w={}, h={}>".format(self.x, self.y)


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return (self == other) == False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<pos x={} y={}>".format(self.x, self.y)

    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def distance_to(self, other):
        return distance(self.x, self.y, other.x, other.y)

    def to_vector(self):
        return Vec(self.x, self.y)

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
