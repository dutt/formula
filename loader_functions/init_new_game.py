from attrdict import AttrDict

from game_states import GameStates
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
from util import Size


def get_constants():
    window_title = "Formula"

    map_size = Size(80, 50)
    camera_size = Size(30, 25)
    game_window_size = Size(camera_size.width * CELL_WIDTH, camera_size.height * CELL_HEIGHT)
    window_size = Size(1200, 1000)

    right_panel_size = Size(150, window_size.height)
    message_log_size = Size(window_size.width - right_panel_size.width, window_size.height - game_window_size.height)
    message_log_text_size = Size(message_log_size.width - 10 * CELL_WIDTH, message_log_size.height - 2 * CELL_HEIGHT)

    room_max_size = 15
    room_min_size = 6
    max_rooms = 10

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    retr = AttrDict({
        "window_title": window_title,
        "window_size": window_size,
        "game_window_size": game_window_size,
        "camera_size": camera_size,
        "map_size": map_size,
        "right_panel_size": right_panel_size,
        "message_log_size": message_log_size,
        "message_log_text_size": message_log_text_size,

        "room_max_size": room_max_size,
        "room_min_size": room_min_size,
        "max_rooms": max_rooms,

        "fov_algorithm": fov_algorithm,
        "fov_light_walls": fov_light_walls,
        "fov_radius": fov_radius,
    })

    return retr


from time_system import TimeSystem
from state_data import StateData
from messages import MessageLog
from components.player import Player
from fov import initialize_fov
from story import StoryLoader, StoryData
from run_planner import RunPlanner
from graphics.font import get_width
from graphics.assets import Assets


def get_game_variables(constants, gfx_data):
    player = Player(gfx_data.assets)
    timesystem = TimeSystem()
    text_width = constants.message_log_text_size.width / get_width(Assets.get().font_message)
    log = MessageLog(text_width)  # for some margin on the sides
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
