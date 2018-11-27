from attrdict import AttrDict

from game_states import GameStates
from graphics.constants import CELL_HEIGHT
from util import Size


def get_constants():
    window_title = "Formula"

    screen_size = Size(80, 50)
    map_size = Size(80, 50)
    camera_size = Size(30, 30)

    bar_width = 20
    bottom_panel_height = 7 * CELL_HEIGHT
    bottom_panel_y = screen_size.height - bottom_panel_height

    window_size = Size(1200, 1000)
    right_panel_size = Size(150, window_size.height - bottom_panel_height)

    message_x = bar_width + 2
    message_size = Size(screen_size.width - bar_width - 2, bottom_panel_height - 1)

    room_max_size = 15
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

    retr = AttrDict({
        "window_title": window_title,
        "window_size": window_size,
        "screen_size": screen_size,
        "camera_size": camera_size,
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
from messages import MessageLog
from components.player import Player
from fov import initialize_fov
from story import StoryLoader, StoryData
from run_planner import RunPlanner


def get_game_variables(constants, gfx_data):
    player = Player(gfx_data.assets)
    timesystem = TimeSystem()
    log = MessageLog(constants.message_x, constants.message_size)
    state = GameStates.WELCOME_SCREEN
    state = GameStates.PLAY
    story_loader = StoryLoader()
    story_data = StoryData(story_loader)
    planner = RunPlanner(3, player, gfx_data.assets, constants, timesystem)
    player.pos = planner.current_map.player_pos
    fov_map = initialize_fov(planner.current_map)
    game_data = StateData(
            player,
            planner.current_map.entities,
            log,
            constants,
            timesystem,
            fov_map,
            fov_recompute=True,
            story_data=story_data,
            run_planner=planner
    )
    return game_data, state
