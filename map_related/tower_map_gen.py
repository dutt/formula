import random
from enum import Enum, auto

from components.drawable import Drawable
from components.stairs import Stairs
from components.entity import Entity
from graphics.assets import Assets
from graphics.render_order import RenderOrder
from map_related.gamemap import GameMap
from map_related.map_util import get_monster
from random_utils import random_choice_from_dict, from_dungeon_level
from util import Pos, Rect


class WallDirection(Enum):
    horizontal = auto()
    vertical = auto()


class DoorDirection(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

# a modfiied version of
# https://gamedev.stackexchange.com/questions/47917/procedural-house-with-rooms-generator

class TowerMapGenerator:

    @staticmethod
    def make_map(constants, level, monster_chances):
        retr = GameMap(constants.map_size, level)
        assets = Assets.get()
        retr.chunks = TowerMapGenerator.chunkify(retr)
        TowerMapGenerator.cleanup_walls(retr)
        TowerMapGenerator.make_doors(retr, retr.chunks)
        TowerMapGenerator.place_monsters(retr, retr.chunks, monster_chances, level, assets)
        TowerMapGenerator.place_stairs(retr, retr.chunks, assets)
        retr.set_tile_info(retr.tiles)

        px = retr.chunks[0].x + retr.chunks[0].width // 2
        py = retr.chunks[0].y + retr.chunks[0].height // 2
        retr.player_pos = Pos(px, py)
        retr.orig_player_pos = Pos(px, py)

        # print_map(retr)

        return retr

    @staticmethod
    def mark_room(m, chunk, room):
        for x in range(chunk.x, chunk.x + chunk.width):
            for y in range(chunk.y, chunk.y + chunk.height):
                m.tiles[x][y].hallway = False
                m.tiles[x][y].room = room
            m.tiles[x][chunk.y].blocked = True
            m.tiles[x][chunk.y].block_sight = True
            m.tiles[x][chunk.y + chunk.height - 1].blocked = True
            m.tiles[x][chunk.y + chunk.height - 1].block_sight = True
        for y in range(chunk.y, chunk.y + chunk.height):
            m.tiles[chunk.x][y].blocked = True
            m.tiles[chunk.x][y].block_sight = True
            m.tiles[chunk.x + chunk.width - 1][y].blocked = True
            m.tiles[chunk.x + chunk.width - 1][y].block_sight = True
        chunk.room = room

    @staticmethod
    def mark_hallway(m, chunk, pos, direction):
        if direction == WallDirection.vertical:
            for y in range(chunk.y, chunk.y + chunk.height):
                m.tiles[pos][y].hallway = True
                m.tiles[pos][y].room = -1
        else:
            for x in range(chunk.x, chunk.x + chunk.width):
                m.tiles[x][pos].hallway = True
                m.tiles[x][pos].room = -1

    @staticmethod
    def pop_largest(chunks):
        size = 0
        retr_idx = None
        for idx, c in enumerate(chunks):
            if c.width * c.height > size:
                size = c.width * c.height
                retr_idx = idx
        retr = chunks.pop(retr_idx)
        return retr

    # first pass. split floor into chunks and hallways
    @staticmethod
    def chunkify(m):
        direction = WallDirection.horizontal
        start_chunk = Rect(0, 0, m.width, m.height)
        TowerMapGenerator.mark_room(m, start_chunk, 0)
        chunks = [start_chunk]
        minsize = 13
        minlength = 6
        while TowerMapGenerator.free_area(m) < TowerMapGenerator.total_size(m) * 0.2:
            curr = TowerMapGenerator.pop_largest(chunks)
            if direction == WallDirection.vertical and curr.width > minsize:
                start = curr.x + max(minlength, int(curr.width * 0.2))
                end = curr.x + curr.width - max(minlength, int(curr.width * 0.2))
                hallway = random.randint(start, end)
                first = Rect(curr.x, curr.y, hallway - curr.x, curr.height)
                second = Rect(hallway + 1, curr.y, curr.x + curr.width - hallway - 1, curr.height)
                new_direction = WallDirection.horizontal
            elif direction == WallDirection.horizontal and curr.height > minsize:  # horizontal
                start = curr.y + max(minlength, int(curr.height * 0.2))
                end = curr.y + curr.height - max(minlength, int(curr.height * 0.2))
                hallway = random.randint(start, end)
                first = Rect(curr.x, curr.y, curr.width, hallway - curr.y)
                second = Rect(curr.x, hallway + 1, curr.width, curr.y + curr.height - hallway - 1)
                new_direction = WallDirection.vertical
            else:  # chunk too small, done. just re-add the chunk
                chunks.append(curr)
                break

            TowerMapGenerator.mark_room(m, first, TowerMapGenerator.first_unused_room_id(m))
            chunks.append(first)

            TowerMapGenerator.mark_room(m, second, TowerMapGenerator.first_unused_room_id(m))
            chunks.append(second)

            TowerMapGenerator.mark_hallway(m, curr, hallway, direction)
            direction = new_direction

        return chunks

    @staticmethod
    def cleanup_walls(m):
        t = m.tiles

        # first remove walls between corridors
        for x in range(2, m.width - 2):
            for y in range(2, m.height - 2):
                if t[x][y - 1].hallway and t[x][y].blocked and t[x][y + 1].hallway:
                    t[x][y].hallway = True
                    t[x][y].blocked = False
                    t[x][y].block_sight = False
                if t[x - 1][y].hallway and t[x][y].blocked and t[x + 1][y].hallway:
                    t[x][y].hallway = True
                    t[x][y].blocked = False
                    t[x][y].block_sight = False

    @staticmethod
    def make_doors(m, chunks):
        def get_choices(c):
            retr = []
            if c.x > 0 and c.width < m.width:
                retr.append(DoorDirection.LEFT)
            if c.y > 0 and c.height < m.height:
                retr.append(DoorDirection.UP)
            if c.y + c.height < m.height:
                retr.append(DoorDirection.DOWN)
            if c.x + c.width < m.width:
                retr.append(DoorDirection.RIGHT)
            return retr

        for c in chunks:
            doors = get_choices(c)
            assert len(doors) > 0
            dir = random.choice(doors)
            xpos = None
            ypos = None
            if dir == DoorDirection.UP:
                xpos = random.randint(c.x + 1, c.x + c.width - 2)
                if c.y == 0:
                    ypos = c.y + c.height - 1
                else:
                    ypos = c.y
            elif dir == DoorDirection.RIGHT:
                if c.x + c.width < m.width:
                    xpos = c.x + c.width - 1
                else:
                    xpos = c.x
                ypos = random.randint(c.y + 1, c.y + c.height - 2)
            elif dir == DoorDirection.DOWN:
                xpos = random.randint(c.x + 1, c.x + c.width - 2)
                if c.y + c.height < m.height:
                    ypos = c.y + c.height - 1
                else:
                    ypos = c.y
            elif dir == DoorDirection.LEFT:
                if c.x > 0:
                    xpos = c.x
                else:
                    xpos = c.x + c.width - 1
                ypos = random.randint(c.y + 1, c.y + c.height - 2)
            assert xpos is not None
            assert ypos is not None
            m.tiles[xpos][ypos].hallway = True
            m.tiles[xpos][ypos].blocked = False
            m.tiles[xpos][ypos].block_sight = False
            m.tiles[xpos][ypos].room = -1

        # then make extra doors through walls crossing the whole map

        # first horisontal walls
        for y in range(1, m.height - 1):
            hallway_found = False
            for x in range(1, m.width - 1):
                if not m.tiles[x][y].blocked:
                    hallway_found = True
            if not hallway_found:
                xpos = random.randint(1, m.width - 2)
                m.tiles[xpos][y].blocked = False
                m.tiles[xpos][y].block_sight = False
                m.tiles[xpos][y].hallway = True
                m.tiles[xpos][y].room = -1

        # first veritical walls
        for x in range(1, m.width - 1):
            hallway_found = False
            for y in range(1, m.height - 1):
                if not m.tiles[x][y].blocked:
                    hallway_found = True
            if not hallway_found:
                ypos = random.randint(1, m.height - 2)
                m.tiles[xpos][y].blocked = False
                m.tiles[xpos][y].block_sight = False
                m.tiles[xpos][y].hallway = True
                m.tiles[xpos][y].room = -1

    @staticmethod
    def place_monsters(m, chunks, monster_chances, level, assets):
        entities = []
        chance_any = monster_chances["any"]
        del monster_chances["any"]
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], level + 1)
        for idx, c in enumerate(chunks):

            rval = random.randint(0, 100)
            if rval > chance_any:
                continue
            if idx == 0:
                num_monsters = 1 # don't overwhelm in the first room
            else:
                num_monsters = random.randint(1, max_monsters_per_room)
            room_center = Pos(c.x + c.width // 2, c.y + c.height // 2)
            skip_room = False

            for i in range(num_monsters):
                x = random.randint(c.x + 1, c.x + c.width - 1)
                y = random.randint(c.y + 1, c.y + c.height - 1)
                if idx == 0:
                    # first room, don't spawn right next to player
                    attempts = 0
                    while Pos(x, y).distance_to(room_center) < 4:
                        x = random.randint(c.x + 1, c.x + c.width - 1)
                        y = random.randint(c.y + 1, c.y + c.height - 1)
                        attempts += 1
                        if attempts > 100:
                            skip_room = True
                if skip_room:
                    continue

                already_there = [entity for entity in entities if entity.pos.x == x and entity.pos.y == y]
                if not any(already_there) and not m.tiles[x][y].blocked:
                    monster_choice = random_choice_from_dict(monster_chances)
                    entities.extend(get_monster(x, y, m, c, monster_choice, assets, entities))

        m.entities = entities

    @staticmethod
    def place_stairs(m, chunks, assets):
        stairs_component = Stairs(m.dungeon_level + 1)
        drawable_component = Drawable(assets.stairs)
        posx = chunks[-1].x + chunks[-1].width // 2
        posy = chunks[-1].y + chunks[-1].height // 2
        down_stairs = Entity(posx, posy, "Stairs",
                             render_order=RenderOrder.STAIRS, stairs=stairs_component, drawable=drawable_component)
        m.entities.append(down_stairs)

    @staticmethod
    def free_area(m):
        count = 0
        for x in range(m.width):
            for y in range(m.height):
                if m.tiles[x][y].hallway:
                    count += 1
        return count

    @staticmethod
    def total_size(m):
        return m.width * m.height

    @staticmethod
    def first_unused_room_id(m):
        curr = 1
        while True:
            found = False
            for x in range(m.width):
                for y in range(m.height):
                    if m.tiles[x][y].room == curr:
                        found = True
                        break
            if not found:
                break
            else:
                curr += 1
        return curr
