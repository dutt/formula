import math

import tcod

from gfx import RenderOrder


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return (self == other) == False


class Entity:
    def __init__(self, x, y, char, color, name, speed=0,
                 blocks=False, render_order=RenderOrder.CORPSE,
                 fighter=None, ai=None, stairs=None, level=None,
                 caster=None):
        self.pos = Pos(int(x), int(y))
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.action_points = 0
        self.speed = speed

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.stairs = stairs
        if self.stairs:
            self.stairs.owner = self

        self.level = level
        if self.level:
            self.level.owner = self

        self.caster = caster
        if self.caster:
            self.caster.owner = self

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<{} at ({},{})>".format(self.name, self.pos.x, self.pos.y)

    def move(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy

    def take_turn(self, game_data):
        if self.ai and self.action_points > 0:
            return self.ai.take_turn(game_data)
        else:
            return None

    def move_towards(self, dest_x, dest_y, game_map, entities):
        dx = dest_x - self.pos.x
        dy = dest_y - self.pos.y

        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.pos.x + dx, self.pos.y + dy) or
                get_blocking_entites_at_location(entities, self.pos.x + dx, self.pos.y + dy)):
            self.move(dx, dy)

    def distance_to(self, other):
        dx = other.pos.x - self.pos.x
        dy = other.pos.y - self.pos.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.pos.x) ** 2 + (y - self.pos.y) ** 2)

    def move_astar(self, target, entities, game_map):
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
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                tcod.map_set_properties(fov, entity.pos.x, entity.pos.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = tcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.pos.x, self.pos.y, target.pos.x, target.pos.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other
        # rooms) if for example the player is in a corridor. It makes sense to keep path size relatively low to keep
        # the monsters from running around the map if there's an alternative path really far away
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.pos.x = x
                self.pos.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths, for example another monster
            # blocks a corridor- It will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.pos.x, target.pos.y, game_map, entities)

            # Delete the path to free memory
        tcod.path_delete(my_path)


def get_blocking_entites_at_location(entities, destx, desty):
    for e in entities:
        if e.blocks and e.pos.x == destx and e.pos.y == desty:
            return e
    return None
