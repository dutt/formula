import pygame
from attrdict import AttrDict

from components.events import EventType
from graphics.assets import Assets
from graphics.window import Window, Label, Clickable, ClickMode
from graphics.textwindow import TextWindow
from graphics.display_helpers import display_text
from util import Pos, Size, resource_path


class InventoryHelpWindow(TextWindow):
    PATH = resource_path("data/help/inventory_window.txt")

    def __init__(self, constants, visible=False):
        super().__init__(constants, visible, path=InventoryHelpWindow.PATH, next_window=None)


class ConsumableMarker(Clickable):
    def __init__(self, consumable, consumable_index, pos, size, parent):
        super().__init__(pos, size, parent=parent, click_mode=ClickMode.LEFT)
        self.consumable = consumable
        self.consumable_index = consumable_index
        self.parent = parent

    def draw(self, surface, game_data, gfx_data):
        coords = (self.pos.x - 5, self.pos.y - 5, 140, 40)
        if self.consumable_index == self.parent.selected:
            pygame.draw.rect(surface, (100, 150, 100), coords, 3)
        else:
            pygame.draw.rect(surface, (25, 50, 25), coords, 3)
        display_text(
            surface, self.consumable.name, gfx_data.assets.font_message, (self.pos.x, self.pos.y),
        )

    def handle_click(self, game_data, gfx_data, mouse_action):
        print(f"Consumable {self.consumable_index} clicked")
        self.parent.selected = self.consumable_index


class QuickslotMarker(Clickable):
    def __init__(self, qs_index, pos, size, parent):
        super().__init__(pos, size, parent=parent, click_mode=ClickMode.LEFT)
        self.qs_index = qs_index
        self.parent = parent

    def draw(self, surface, game_data, gfx_data):
        display_text(
            surface, "Slot {}".format(self.qs_index + 1), gfx_data.assets.font_message, (self.pos.x, self.pos.y),
        )
        item = game_data.inventory.get_quickslot(self.qs_index)
        square_y = self.pos.y + 35
        coords = (self.pos.x - 5, square_y - 5, self.parent.slot_width, 40)
        pygame.draw.rect(surface, (150, 150, 150), coords, 3)
        if item:
            display_text(surface, item.name, gfx_data.assets.font_message, (self.pos.x, square_y))

    def handle_click(self, game_data, gfx_data, mouse_action):
        print(f"Quickslot {self.qs_index} clicked")
        game_data.inventory.set_quickslot(self.qs_index, game_data.inventory.items[self.parent.selected])


class InventoryWindow(Window):
    def __init__(self, constants, visible=False):
        super().__init__(
            constants.helper_window_pos, constants.helper_window_size, visible, click_mode=ClickMode.LEFT,
        )
        self.title = Label(Pos(200, 25), "Inventory")
        self.quickslots_label = Label(Pos(200, 410), "Quickslots")
        self.selected = 0
        self.items_per_row = 2
        self.num_quickslots = constants.num_quickslots
        self.slot_width = 140
        self.consumable_markers = []
        self.quickslot_markers = []

    def init(self, game_data, gfx_data):
        # first items
        self.consumable_markers = []
        x = self.pos.x + 30
        y = self.pos.y + 30
        for idx, item in enumerate(game_data.inventory.items):
            cm = ConsumableMarker(item, idx, pos=Pos(x, y), size=Size(self.slot_width, 50), parent=self)
            self.consumable_markers.append(cm)
            x += 150
            if idx % self.items_per_row == 0:
                y += 60
                x = self.pos.x + 30

        # then quickslots
        self.quickslot_markers = []
        x = self.pos.x + 10
        y = 410
        for qs in range(self.num_quickslots):
            qm = QuickslotMarker(qs, pos=Pos(x, y), size=Size(self.slot_width, 50), parent=self)
            self.quickslot_markers.append(qm)
            x += self.slot_width + 20

    def draw_quickslots(self, surface, game_data, gfx_data):
        x = self.pos.x + 10
        y = 410

        y += 40
        for qs in range(self.num_quickslots):
            item = game_data.inventory.get_quickslot(qs)
            display_text(surface, "Slot {}".format(qs + 1), gfx_data.assets.font_message, (x, y))
            square_y = y + 35
            coords = (x - 5, square_y - 5, self.slot_width, 40)
            pygame.draw.rect(surface, (150, 150, 150), coords, 3)
            if item:
                display_text(surface, item.name, gfx_data.assets.font_message, (x, square_y))
            x += self.slot_width + 20

    def draw(self, game_data, gfx_data):
        surface = pygame.Surface(self.size.tuple())

        self.title.draw(surface)

        for cm in self.consumable_markers:
            cm.draw(surface, game_data, gfx_data)

        self.quickslots_label.draw(surface)
        for qm in self.quickslot_markers:
            qm.draw(surface, game_data, gfx_data)

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
            self.selected = min(self.selected + self.items_per_row, len(game_data.inventory.items) - 1)

        right = key_action.get("right")
        if right:
            self.selected = min(self.selected + 1, len(game_data.inventory.items) - 1)

        left = key_action.get("left")
        if left:
            self.selected = max(0, self.selected - 1)

        assign = key_action.get("assign")
        if assign:
            self.set_quickslot(assign - 1, game_data)

    def handle_click(self, game_data, gfx_data, mouse_action):
        for cm in self.consumable_markers:
            if cm.is_clicked(mouse_action):
                return cm.handle_click(game_data, gfx_data, mouse_action)

        for qm in self.quickslot_markers:
            if qm.is_clicked(mouse_action):
                return qm.handle_click(game_data, gfx_data, mouse_action)
