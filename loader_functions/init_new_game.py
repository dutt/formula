import pygame
from attrdict import AttrDict

from components.game_states import GameStates
from graphics.camera import Camera
from graphics.constants import CELL_WIDTH, CELL_HEIGHT
from graphics.formula_window import FormulaWindow, FormulaHelpWindow
from graphics.game_window import GameWindow
from graphics.message_log_window import MessageLogWindow
from graphics.minor_windows import (
    GeneralHelpWindow,
    AskQuitWindow,
    DeadWindow,
    VictoryWindow,
)
from graphics.right_panel_window import RightPanelWindow
from graphics.story_window import StoryWindow, StoryHelpWindow
from graphics.level_up_window import LevelUpWindow
from graphics.console_window import ConsoleWindow
from graphics.crafting_window import CraftingWindow, CraftingHelpWindow
from graphics.inventory_window import InventoryWindow, InventoryHelpWindow
from graphics.visual_effect import VisualEffectSystem
from graphics.window_manager import WindowManager
from util import Size, Pos


def get_constants():
    window_title = "Formula"

    map_size = Size(40, 30)
    camera_size = Size(25, 20)
    game_window_size = Size((camera_size.width + 1) * CELL_WIDTH, (camera_size.height + 1) * CELL_HEIGHT)
    window_size = Size(150 + game_window_size.width, 900)

    right_panel_size = Size(150, window_size.height)
    message_log_size = Size(window_size.width - right_panel_size.width, window_size.height - game_window_size.height,)
    message_log_text_size = Size(message_log_size.width - 2 * CELL_WIDTH, message_log_size.height - 2 * CELL_HEIGHT,)

    helper_window_size = Size(800, 600)
    helper_window_pos = Pos(100, 100)

    num_consumables = 5
    num_quickslots = 3

    room_max_size = 15
    room_min_size = 6
    max_rooms = 5

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    retr = AttrDict(
        {
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
            "num_consumables": num_consumables,
            "num_quickslots": num_quickslots,
        }
    )

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


from components.player import Player
from components.state_data import StateData
from components.formula import Formula
from components.ingredients import Ingredient
from systems.time_system import TimeSystem
from systems.messages import MessageLog
from systems.story import StoryLoader, StoryData
from systems.run_planner import RunPlanner
from systems.formula_builder import FormulaBuilder
from systems.ingredient_storage import IngredientStorage
from systems.inventory import Inventory
from graphics.font import get_width
from graphics.assets import Assets
import config


def setup_data_state(constants):
    pygame.init()
    pygame.display.set_caption("Formula")
    pygame.mixer.quit()
    pygame.key.set_repeat(200)
    main = pygame.display.set_mode((constants.window_size.width, constants.window_size.height))

    assets = Assets.setup()

    run_tutorial = True
    godmode = False

    fps_per_second = 30

    story_loader = StoryLoader()
    story_data = StoryData(story_loader)

    timesystem = TimeSystem()

    visuals = VisualEffectSystem.setup(fps_per_second)

    clock = pygame.time.Clock()

    windows = WindowManager()
    rpw = RightPanelWindow(constants)
    windows.push(rpw)
    windows.push(GameWindow(constants, parent=rpw))
    windows.push(MessageLogWindow(constants, parent=rpw))

    windows.push(StoryWindow(constants, story_data, visible=True))
    windows.push(StoryHelpWindow(constants))
    windows.push(FormulaWindow(constants))
    windows.push(FormulaHelpWindow(constants))
    windows.push(GeneralHelpWindow(constants))
    windows.push(LevelUpWindow(constants))
    windows.push(AskQuitWindow(constants))
    windows.push(DeadWindow(constants))
    windows.push(VictoryWindow(constants))
    windows.push(ConsoleWindow(constants))
    windows.push(CraftingWindow(constants))
    windows.push(CraftingHelpWindow(constants))
    windows.push(InventoryWindow(constants))
    windows.push(InventoryHelpWindow(constants))

    text_width = constants.message_log_text_size.width / get_width(Assets.get().font_message)
    log = MessageLog(text_width)  # for some margin on the sides

    player = Player(godmode)
    formula_builder = FormulaBuilder(player.caster.num_slots, player.caster.num_formulas, run_tutorial)

    levels = 9
    planner = RunPlanner(levels, player, constants, timesystem, run_tutorial)
    fov_map = None

    ingredient_storage = IngredientStorage()
    if config.conf.pickupstartcount == "base":
        ingredient_storage.add_multiple(
            {Ingredient.FIRE: 2, Ingredient.WATER: 2, Ingredient.EARTH: 2, Ingredient.RANGE: 1, Ingredient.AREA: 1,}
        )
        if config.conf.trap:
            ingredient_storage.add_multiple(
                {Ingredient.TRAP: 2,}
            )
    else:
        for ing in Ingredient.all():
            ingredient_storage.add_multiple({ing: config.conf.pickupstartcount})

    menu_data = AttrDict({"currchoice": 0})

    inventory = Inventory(max_count=constants.num_consumables, num_quickslots=constants.num_quickslots)
    from components.consumable import Firebomb, Freezebomb, Teleporter, CooldownClear

    # for t in [Firebomb, Freezebomb, Teleporter, CooldownClear, Thingy, Thingmajig]:
    #    inventory.add(t())
    inventory.add(Firebomb())
    inventory.add(Teleporter())

    initial_state = GameStates.STORY_SCREEN

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
        menu_data=menu_data,
        initial_state=initial_state,
        initial_state_history=[GameStates.PLAY],
        ingredient_storage=ingredient_storage,
        inventory=inventory,
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
        windows=windows,
    )

    if not run_tutorial:
        game_data.prev_state = [GameStates.FORMULA_SCREEN, GameStates.PLAY]
        windows.activate_wnd_for_state(game_data.state, game_data, gfx_data)
        story_data.next_story()

    # create default formulas
    Formula.EMPTY, _ = formula_builder.get_empty_formula(caster=player)
    initial_formulas = formula_builder.evaluate_entity(caster=player)
    player.caster.set_formulas(initial_formulas)

    return game_data, gfx_data, initial_state
