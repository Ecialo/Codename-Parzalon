from itertools import chain
import consts
from cocos import layer
from cocos.scene import Scene
from cocos import tiles
from cocos import sprite
from non_scroll_rect_map import No_Scroll_Rect_Map_Layer
import items
import cocos
import pyglet
empty = pyglet.image.SolidColorImagePattern((255, 255, 255, 255)).create_image(32, 32)

MAX_INVENTORY_SIZE = 5


class Bag(No_Scroll_Rect_Map_Layer):

    is_event_handler = True

    def __init__(self, master):
        super(Bag, self).__init__(-1, 32, 32,
                                  [[tiles.RectCell(i, j, 32, 32, {}, tiles.Tile(-1, {}, empty))
                                    for j in xrange(MAX_INVENTORY_SIZE)]
                                  for i in xrange(MAX_INVENTORY_SIZE)])
        self.master = master
        #self.origin_x = 400#16*MAX_INVENTORY_SIZE
        #self.origin_y = 0#16*MAX_INVENTORY_SIZE

        self.prev_cell = None
        self.selected_cell = None

    def put_item(self, item):
        print item
        for cell in chain(*self.cells):
            if cell.tile.id == -1:
                print cell.i, cell.j
                cell.tile = item.inventory_representation
                self.update_cell(cell)
                return

    def swap_items_in_cells(self, cell_1, cell_2):
        cell_1.tile, cell_2.tile = cell_2.tile, cell_1.tile
        self.update_cell(cell_1)
        self.update_cell(cell_2)

    def on_enter(self):
        self.origin_x, self.origin_y = self.position
        super(Bag, self).on_enter()

    def on_mouse_motion(self, x, y, dx, dy):
        prev_cell = self.prev_cell
        cell = self.get_at_pixel(x, y)
        if prev_cell:
            i, j = prev_cell.i, prev_cell.j
            self.set_cell_opacity(i, j, 255)
        if cell:
            i, j = cell.i, cell.j
            self.set_cell_opacity(i, j, 126)
        self.prev_cell = cell

    def on_mouse_press(self, x, y, buttons, modifers):
        if self.selected_cell is None:
            self.selected_cell = self.get_at_pixel(x, y)
        else:
            n_cell = self.get_at_pixel(x, y)
            self.swap_items_in_cells(self.selected_cell, n_cell)
            self.selected_cell = None


class Inventory(layer.Layer):

    is_event_handler = True

    def __init__(self, master):
        super(Inventory, self).__init__()
        self.master = master
        self.main_item = None
        self.secondary_item = None
        self.armor = {}     # key is item.slot
        self.bag = Bag(master)

        buddy = sprite.Sprite('inventory.png')
        buddy.position = (400, 400)
        self.bag.position = (400, 0)

        self.add(buddy)
        self.add(self.bag, z=1)

    def put_item(self, item):
        if item.size is items.SMALL:
            self.bag.put_item(item)
        else:
            self.change_item(item)

    def open(self):
        self.master.get_ancestor(Scene).add(self, z=5)
        # for cell in chain(*self.bag.cells):
        #     print cell.tile, cell.i, cell.j

    def close(self):
        self.kill()

    def change_item(self, item):
        if item.slot is consts.HAND:
            item_to_drop = self.main_item
            self.main_item = item
        else:
            item_to_drop = self.armor[item.slot]
            self.armor[item.slot] = item
        item_to_drop.drop()

    def drop_item(self, item):
        item.drop()


