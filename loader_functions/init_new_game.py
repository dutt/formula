from attrdict import AttrDict as attribdict

from game_states import GameStates
from util import Size


def get_constants():
    window_title = "Formula"

    window_size = Size(1200, 1000)
    screen_size = Size(80, 50)
    map_size = Size(70, 43)

    bar_width = 20
    bottom_panel_height = 7
    bottom_panel_y = screen_size.height - bottom_panel_height

    right_panel_size = Size(150, screen_size.height - bottom_panel_height)

    message_x = bar_width + 2
    message_size = Size(screen_size.width - bar_width - 2, bottom_panel_height - 1)

    room_max_size = 10
    room_min_size = 6
    max_rooms = 10

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        "dark_wall": (30, 30, 30),
        "dark_ground": (60, 60, 60),
        "light_wall": (90, 90, 90),
        "light_ground": (140, 140, 140)
    }

    retr = attribdict({
        "window_title": window_title,
        "window_size": window_size,
        "screen_size": screen_size,
        "map_size": map_size,

        "bar_width": bar_width,
        "bottom_panel_height": bottom_panel_height,
        "bottom_panel_y": bottom_panel_y,

        "right_panel_size": right_panel_size,

        "message_x": message_x,
        "message_size": message_size,

        "room_max_size": room_max_size,
        "room_min_size": room_min_size,
        "max_rooms": max_rooms,

        "fov_algorithm": fov_algorithm,
        "fov_light_walls": fov_light_walls,
        "fov_radius": fov_radius,

        "colors": colors
    })

    return retr


from time_system import TimeSystem
from state_data import StateData
from gamemap import GameMap
from messages import MessageLog
from components.player import Player
from fov import initialize_fov


def get_game_variables(constants, gfx_data):
    player = Player(gfx_data.assets)
    entities = [player]
    timesystem = TimeSystem()
    timesystem.register(player)
    gmap = GameMap(constants.map_size, gfx_data.assets)
    gmap.make_map(constants, player, entities, timesystem)
    log = MessageLog(constants.message_x, constants.message_size)
    state = GameStates.WELCOME_SCREEN
    #state = GameStates.PLAY
    fov_map = initialize_fov(gmap)

    game_data = StateData(
            player,
            entities,
            gmap,
            log,
            constants,
            timesystem,
            fov_map,
            fov_recompute=True
    )
    return game_data, state
