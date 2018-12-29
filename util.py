import math
import os
import sys

import tcod


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

    def to_pos(self):
        return Pos(self.x, self.y)

    def tuple(self):
        return self.x, self.y

    def __mul__(self, other):
        if type(other) == Vec:
            return Vec(self.x * other.x, self.y * other.y)
        else:
            return Vec(self.x * other, self.y * other)

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<vec w={}, h={}>".format(self.x, self.y)

    def __hash__(self):
        return self.tuple().__hash__()


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<pos x={} y={}>".format(self.x, self.y)

    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def __hash__(self):
        return self.tuple().__hash__()

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


def get_line(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


def find_path(source, target, entities, game_map):
    # Create a FOV map that has the dimensions of the map
    fov = tcod.map_new(game_map.width, game_map.height)

    # Scan the current map each turn and set all the walls as unwalkable
    for y1 in range(game_map.height):
        for x1 in range(game_map.width):
            tcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                    not game_map.tiles[x1][y1].blocked)

    # Scan all the objects to see if there are objects that must be navigated around
    # Check also that the object isn't self or the target (so that the start and the end points are free)
    # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
    for entity in entities:
        if entity.blocks and entity != source and entity != target:
            # Set the tile as a wall so it must be navigated around
            tcod.map_set_properties(fov, entity.pos.x, entity.pos.y, True, False)

    # Allocate a A* path
    # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
    my_path = tcod.path_new_using_map(fov, 0.0)

    # Compute the path between self's coordinates and the target's coordinates
    tcod.path_compute(my_path, source.pos.x, source.pos.y, target.pos.x, target.pos.y)

    # Check if the path exists, and in this case, also the path is shorter than 25 tiles
    # The path size matters if you want the monster to use alternative longer paths (for example through other
    # rooms) if for example the player is in a corridor. It makes sense to keep path size relatively low to keep
    # the monsters from running around the map if there's an alternative path really far away
    has_path = not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25

    # Delete the path to free memory
    tcod.path_delete(my_path)

    return has_path
