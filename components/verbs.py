import tcod

from util import get_line, find_path


def can_move_towards_player(monster, game_data):
    if not can_see_player(monster, game_data):
        return False
    vec = monster.pos - game_data.player.pos
    if vec.length() < 2:
        return False
    return find_path(monster, game_data.player, game_data.map.entities, game_data.map)


def can_see_player(monster, game_data, visibility=10):

    visible = tcod.map_is_in_fov(game_data.fov_map, monster.pos.x, monster.pos.y)
    return visible

    """
    this doesn't work nicely yet for some corners, player can see monster but monster can't see player
    in situations like this, M=monster, P=player, = are walls 
    
    M
    = =
     P
     
    This is because the lines goes directly down first, crossing the wall and thus being blocked 
    """
    vec = monster.pos - game_data.player.pos
    if vec.length() > visibility:
        return False
    points = get_line(monster.pos.tuple(), game_data.player.pos.tuple())
    for p in points:
        x, y = p
        if game_data.map.tiles[x][y].block_sight:
            return False
    return True


def can_attack_player(monster, game_data, min_dist=0, max_dist=1.5):
    if not can_see_player(monster, game_data):
        return False
    if game_data.player.fighter.hp <= 0:
        return False
    vec = monster.pos - game_data.player.pos
    return min_dist <= vec.length() <= max_dist
