import tcod
from attrdict import AttrDict as attribdict

from game_states import GameState
from util import Size


def get_constants():
    window_title = "spellmaker"

    screen_size = Size(80, 50)
    map_size = Size(70, 43)

    bar_width = 20
    bottom_panel_height = 7
    bottom_panel_y = screen_size.height - bottom_panel_height

    right_panel_size = Size(10, screen_size.height - bottom_panel_height)

    message_x = bar_width + 2
    message_size = Size(screen_size.width - bar_width - 2, bottom_panel_height - 1)

    room_max_size = 10
    room_min_size = 6
    max_rooms = 20

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        "dark_wall": tcod.Color(30, 30, 30),
        "dark_ground": tcod.Color(60, 60, 60),
        "light_wall": tcod.Color(90, 90, 90),
        "light_ground": tcod.Color(140, 140, 140)
    }

    retr = attribdict({
        "window_title": window_title,
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


from entity import Entity
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equippable import Equippable
from components.equipment import Equipment
from components.equipmentslots import EquipmentSlots
from components.caster import Caster

import gfx
from gamemap import GameMap
from messages import MessageLog


def get_game_variables(constants):
    caster_component = Caster(num_slots=3, num_spells=3)
    fighter_component = Fighter(hp=100, defense=1, power=3)
    inventory_component = Inventory(capacity=3)
    level_component = Level()
    equipment_component = Equipment()
    player = Entity(0, 0, '@', tcod.white, "Player", blocks=True, render_order=gfx.RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component, level=level_component,
                    equipment=equipment_component, caster=caster_component)
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    dagger = Entity(0, 0, '-', tcod.sky, "Dagger", equippable=equippable_component)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)
    entities = [player]
    gmap = GameMap(constants.map_size)
    gmap.make_map(constants.room_min_size, constants.room_max_size, constants.max_rooms, constants.map_size, player,
                  entities)
    log = MessageLog(constants.message_x, constants.message_size)
    state = GameState.WELCOME_SCREEN

    return player, entities, gmap, log, state
