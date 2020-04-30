import pygame

from components.events import EventType
from graphics.assets import Assets
from graphics.window import Window, Label
from graphics.display_helpers import display_text
from util import Pos

class InventoryWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(constants.helper_window_pos, constants.helper_window_size, visible)
        self.title = Label(Pos(200,25), "Inventory")
        self.quickslots_label = Label(Pos(200, 410), "Quickslots")
        self.selected = 0
        self.items_per_row = 2
        self.num_quickslots = constants.num_quickslots
        self.slot_width = 140

    def draw_consumable(self, surface, gfx_data, x,y, consumable, index):
        coords = (x-5, y-5, 140, 40)
        if index == self.selected:
            pygame.draw.rect(surface, (100, 150, 100), coords, 3)
        display_text(surface, consumable.name, gfx_data.assets.font_message, (x,y))

    def draw_quickslots(self, surface, game_data, gfx_data):
        x = 50
        y = 410
        self.quickslots_label.draw(surface)

        y += 40
        for qs in range(self.num_quickslots):
            item = game_data.inventory.get_quickslot(qs)
            display_text(surface, "Slot {}".format(qs+1), gfx_data.assets.font_message, (x,y))
            square_y = y + 35
            coords = (x-5, square_y-5, self.slot_width, 40)
            pygame.draw.rect(surface, (150, 150, 150), coords, 3)
            if item:
                display_text(surface, item.name, gfx_data.assets.font_message, (x,square_y))
            x += self.slot_width + 20

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())

        self.title.draw(surface)

        x = self.pos.x + 30
        y = self.pos.y + 30
        count = 0
        for idx, item in enumerate(game_data.inventory.items):
            self.draw_consumable(surface, gfx_data, x, y, item, idx)
            x += 130
            count += 1
            if count >= self.items_per_row:
                y += 60
                x = self.pos.x + 30
                count = 0

        self.draw_quickslots(surface, game_data, gfx_data)

        gfx_data.main.blit(surface, self.pos.tuple())

    def set_quickslot(self, quickslot_index, game_data):
        if quickslot_index >= self.num_quickslots:
            return
        game_data.inventory.set_quickslot(quickslot_index, game_data.inventory.items[self.selected])

    def handle_key(self, game_data, gfx_data, key_action):
        close = key_action.get(EventType.exit)
        if close:
            return self.close(game_data, activate_for_new_state=True)

        up = key_action.get("up")
        if up:
            self.selected = max(0, self.selected - self.items_per_row)

        down = key_action.get("down")
        if down:
            self.selected = min(self.selected + self.items_per_row, len(game_data.inventory.items)-1)

        right = key_action.get("right")
        if right:
            self.selected = min(self.selected + 1, len(game_data.inventory.items)-1)

        left = key_action.get("left")
        if left:
            self.selected = max(0, self.selected - 1)

        assign = key_action.get("assign")
        if assign:
            self.set_quickslot(assign-1, game_data)
