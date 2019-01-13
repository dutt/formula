import pygame
from attrdict import AttrDict

from game_states import GameStates
from graphics.camera import Camera
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
from graphics.formula_window import FormulaWindow, FormulaHelpWindow
from graphics.game_window import GameWindow
from graphics.message_log_window import MessageLogWindow
from graphics.minor_windows import WelcomeWindow, GeneralHelpWindow
from graphics.right_panel_window import RightPanelWindow
from graphics.story_window import StoryWindow, StoryHelpWindow
from graphics.level_up_window import LevelUpWindow
from graphics.visual_effect import VisualEffectSystem
from graphics.window_manager import WindowManager
from graphics.setup_window import SetupWindow
from util import Size, Pos


def get_constants():
    window_title = "Formula"

    map_size = Size(40, 30)
    camera_size = Size(30, 25)
    game_window_size = Size((camera_size.width+1) * CELL_WIDTH, (camera_size.height+1) * CELL_HEIGHT)
    window_size = Size(150 + game_window_size.width, 1020)

    right_panel_size = Size(150, window_size.height)
    message_log_size = Size(window_size.width - right_panel_size.width, window_size.height - game_window_size.height)
    message_log_text_size = Size(message_log_size.width - 10 * CELL_WIDTH, message_log_size.height - 2 * CELL_HEIGHT)

    helper_window_size = Size(800, 600)
    helper_window_pos = Pos(200, 200)

    room_max_size = 15
    room_min_size = 6
    max_rooms = 5

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
        "helper_window_size": helper_window_size,
        "helper_window_pos": helper_window_pos,

        "room_max_size": room_max_size,
        "room_min_size": room_min_size,
        "max_rooms": max_rooms,

        "fov_algorithm": fov_algorithm,
        "fov_light_walls": fov_light_walls,
        "fov_radius": fov_radius,
    })

    return retr


class GfxState:
    def __init__(self, main, assets, camera, fullscreen, visuals, fps_per_second, clock, windows):
        self.main = main
        self.assets = assets
        self.camera = camera
        self.fullscreen = fullscreen
        self.visuals = visuals
        self.fps_per_second = fps_per_second
        self.clock = clock
        self.windows = windows


from time_system import TimeSystem
from state_data import StateData
from messages import MessageLog
from components.player import Player
from story import StoryLoader, StoryData
from run_planner import RunPlanner
from graphics.font import get_width
from graphics.assets import Assets
from formula_builder import FormulaBuilder


def setup_data_state(constants):
    state = GameStates.SETUP
    #state = GameStates.FORMULA_SCREEN
    #state = GameStates.PLAY

    story_loader = StoryLoader()
    story_data = StoryData(story_loader)
    timesystem = TimeSystem()

    pygame.init()
    pygame.display.set_caption("Formulas")
    pygame.mixer.quit()
    main = pygame.display.set_mode((constants.window_size.width, constants.window_size.height))

    assets = Assets()
    fps_per_second = 30
    visuals = VisualEffectSystem(fps_per_second)
    clock = pygame.time.Clock()

    windows = WindowManager()
    gw = GameWindow(constants)
    windows.push(gw)
    windows.push(RightPanelWindow(constants, parent=gw))
    windows.push(MessageLogWindow(constants, parent=gw))
    windows.push(WelcomeWindow(constants, state == GameStates.WELCOME_SCREEN))
    windows.push(StoryWindow(constants, state == GameStates.STORY_SCREEN, story_data))
    windows.push(StoryHelpWindow(constants))
    windows.push(FormulaWindow(constants, state == GameStates.FORMULA_SCREEN))
    windows.push(FormulaHelpWindow(constants))
    windows.push(GeneralHelpWindow(constants))
    windows.push(LevelUpWindow(constants))
    windows.push(SetupWindow(constants, visible=True))

    text_width = constants.message_log_text_size.width / get_width(Assets.get().font_message)
    log = MessageLog(text_width)  # for some margin on the sides

    player = Player()
    formula_builder = FormulaBuilder(player.caster.num_slots, player.caster.num_formulas)

    planner = RunPlanner(9, player, constants, timesystem)
    fov_map = None

    menu_data = AttrDict({
        "currchoice": 0
    })

    game_data = StateData(
            player,
            log,
            constants,
            timesystem,
            fov_map,
            fov_recompute=True,
            story_data=story_data,
            run_planner=planner,
            formula_builder=formula_builder,
            menu_data=menu_data
    )

    camera = Camera(constants.camera_size.width, constants.camera_size.height, game_data)

    gfx_data = GfxState(
            main=main,
            assets=assets,
            camera=camera,
            fullscreen=False,
            visuals=visuals,
            fps_per_second=fps_per_second,
            clock=clock,
            windows=windows
    )

    return game_data, gfx_data, state
