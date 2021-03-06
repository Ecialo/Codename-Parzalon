# -*- coding: utf-8 -*-
from itertools import chain

from cocos import layer
from cocos.scene import Scene
from cocos import tiles
from cocos import sprite
from cocos import menu
import pyglet
from pyglet.window import mouse
from non_scroll_rect_map import No_Scroll_Rect_Map_Layer


empty = pyglet.image.SolidColorImagePattern((255, 255, 255, 255)).create_image(32, 32)

from registry.inventory import *
from registry.item import SMALL


class Item_Context_Menu(menu.Menu):
    def __init__(self, item, item_drop_method):
        super(Item_Context_Menu, self).__init__()
        self.item = item
        self.drop_method = item_drop_method
        items = [menu.MenuItem("Drop", self.drop),
                 menu.MenuItem("Close", self.kill)]
        self.create_menu(items)

    def drop(self):
        self.drop_method()
        self.kill()

    def on_enter(self):
        super(Item_Context_Menu, self).on_enter()
        self.parent.lock()

    def on_exit(self):
        super(Item_Context_Menu, self).on_exit()
        self.parent.unlock()


class Belt_Cell(tiles.RectCell):
    def __init__(self, i):
        j = MAX_INVENTORY_SIZE + SEPARATE_ROW_SIZE
        super(Belt_Cell, self).__init__(i, j, INVENTORY_CELL_SIZE, INVENTORY_CELL_SIZE,
                                        {'is_belt': True}, tiles.Tile(-1, {}, empty))


class Inventory_Cell(tiles.RectCell):
    def __init__(self, i, j):
        super(Inventory_Cell, self).__init__(i, j, INVENTORY_CELL_SIZE, INVENTORY_CELL_SIZE,
                                             {'is_inventory': False}, tiles.Tile(-1, {}, empty))


class Locked_Cell(tiles.RectCell):
    def __init__(self, i, j):
        super(Locked_Cell, self).__init__(i, j, INVENTORY_CELL_SIZE, INVENTORY_CELL_SIZE, {}, None)


class Belt(object):
    def __init__(self, size):
        self.size = size
        self.items = [None for i in xrange(MAX_INVENTORY_SIZE)]
        self.current = 0     # index for slots

    def update_size(self, size):
        if size < self.size:
            self.current = 0
        self.size = size

    def select_secondary_item(self, scroll):
        self.current = (self.current + scroll) % self.size
        return self.items[self.current]

    def set_new_item(self, item, index):
        self.items[index] = item


class Bag(No_Scroll_Rect_Map_Layer):
    is_event_handler = False

    def __init__(self, master):

        cells = []
        for i in xrange(MAX_INVENTORY_SIZE):
            column = []
            for j in xrange(MAX_INVENTORY_SIZE + SEPARATE_ROW_SIZE + BELT_ROW_SIZE):
                if j < MAX_INVENTORY_SIZE:
                    column.append(Inventory_Cell(i, j))
                else:
                    column.append(Locked_Cell(i, j))
            cells.append(column)

        super(Bag, self).__init__(-1, INVENTORY_CELL_SIZE, INVENTORY_CELL_SIZE, cells)
        self.belt = Belt(0)
        self.master = master
        self.set_belt_size(3)

    def select_secondary_item(self, scroll):
        return self.belt.select_secondary_item(scroll)

    def put_item(self, item):
        for cell in chain(*self.cells):
            if cell.tile.id == -1:
                cell.tile = item.inventory_representation
                self.update_cell(cell)
                return
        else:
            item.drop()

    def swap_items_in_cells(self, cell_1, cell_2):
        if cell_1 and cell_2:
            cell_1.tile, cell_2.tile = cell_2.tile, cell_1.tile
            self.update_cell(cell_1)
            self.update_cell(cell_2)

    def drop_item(self, cell):
        i, j = cell.i, cell.j
        item = cell.get('item')
        is_belt = cell.get('is_belt')
        if item:
            item.drop()
            if is_belt:
                self.cells[i][j] = Belt_Cell(i, j)
            else:
                self.cells[i][j] = Inventory_Cell(i, j)
            self.update_cell(self.cells[i][j])

    def set_new_belt_item(self, cell):
        self.belt.set_new_item(cell.get('item'), cell.i)

    def set_belt_size(self, belt_size):
        old_belt_size = self.belt.size
        if old_belt_size > belt_size:
            l = belt_size
            r = old_belt_size
            for i in xrange(l, r):
                n_cell = Locked_Cell(i, BELT_CELL)
                content = self.cells[i][Belt_Cell].get('item')
                self.cells[i][Belt_Cell] = n_cell
                self.put_item(content)
                self.update_cell(n_cell)
        elif old_belt_size < belt_size:
            l = old_belt_size
            r = belt_size
            for i in xrange(l, r):
                n_cell = Belt_Cell(i)
                self.cells[i][BELT_CELL] = n_cell
                self.update_cell(n_cell)
        self.belt.update_size(belt_size)

    def destroy(self):
        for cell in chain(*self.cells):
            if cell.tile.id != -1:
                cell.get('item').drop()

    def on_enter(self):
        self.origin_x, self.origin_y = self.position
        super(Bag, self).on_enter()


class Inventory(layer.Layer):
    is_event_handler = True

    def __init__(self, master):
        super(Inventory, self).__init__()
        self._locked = False
        self.master = master
        self.main_item = None
        self.secondary_item = None
        self.armor = {}     # key is item.slot
        self.bag = Bag(master)

        self.selected_cell = None
        self.prev_cell = None
        self.main_item_representation = sprite.Sprite(empty)
        self.main_item_representation.position = (200, 400)
        self.bag.position = (400, 0)
        self.active_zones = [(self.main_item_representation.get_rect(), "main_item")]

        self.add(self.main_item_representation, z=1)
        self.add(self.bag, z=1)

    def put_item(self, item):
        item.set_master(self.master)
        if item.size is SMALL:
            self.bag.put_item(item)
        else:
            self.change_item(item)

    def open(self):
        self.master.get_ancestor(Scene).add(self, z=5)

    def close(self):
        self.kill()

    def select_secondary_item(self, scroll=0):
        self.master.stop_interact_with_item(self.secondary_item)
        self.secondary_item = self.bag.select_secondary_item(scroll)
        self.master.start_interact_with_item(self.secondary_item)

    def set_new_main_item(self, item):
        self.main_item = item
        item_image = item.image
        width, height = item_image.width, item_image.height
        self.main_item_representation.image = item.image
        self.main_item_representation.image_anchor = (width / 2, height / 2)

    def change_item(self, item):
        self.master.start_interact_with_item(item)
        if item.slot is HAND:
            item_to_drop = self.main_item
            self.set_new_main_item(item)
        else:
            item_to_drop = self.armor[item.slot]
            self.armor[item.slot] = item
        if item_to_drop:
            item_to_drop.drop()

    def drop_item(self, item_cell):
        self.bag.drop_item(item_cell)
        if item_cell.get('is_belt'):
            self.bag.set_new_belt_item(item_cell)
            self.select_secondary_item()

    def get_item_outside_bag(self, x, y):
        for item_zone, item_slot in self.active_zones:
            if item_zone.contains(x, y):
                return self.get_item_from_slot(item_slot)

    def get_item_from_slot(self, slot):
        if slot == 'main_item':
            return self.main_item

    def item_dropper(self, item_cell):

        def dropper():
            self.drop_item(item_cell)

        return dropper

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def destroy(self):
        self.bag.destroy()
        self.main_item.drop()

    def on_mouse_motion(self, x, y, dx, dy):
        if not self._locked:
            prev_cell = self.prev_cell
            cell = self.bag.get_at_pixel(x, y)
            if prev_cell and prev_cell.tile:
                i, j = prev_cell.i, prev_cell.j
                self.bag.set_cell_opacity(i, j, 255)
            if cell and cell.tile:
                i, j = cell.i, cell.j
                self.bag.set_cell_opacity(i, j, 126)
            self.prev_cell = cell

    def on_mouse_press(self, x, y, buttons, modifers):
        if not self._locked:
            if buttons & mouse.RIGHT:
                cell = self.bag.get_at_pixel(x, y)
                if cell:
                    item = cell.get('item')
                    if item:
                        self.add(Item_Context_Menu(item, self.item_dropper(cell)), z=2)
                else:
                    item = self.get_item_outside_bag(x, y)
                    if item:
                        self.add(Item_Context_Menu(item, None), z=2)
            elif not self.selected_cell:
                self.selected_cell = self.bag.get_at_pixel(x, y)
            else:
                n_cell = self.bag.get_at_pixel(x, y)
                self.bag.swap_items_in_cells(self.selected_cell, n_cell)
                if n_cell.get('is_belt'):
                    self.bag.set_new_belt_item(n_cell)
                if self.selected_cell.get('is_belt'):
                    self.bag.set_new_belt_item(self.selected_cell)
                self.select_secondary_item()
                self.selected_cell = None

    def transfer(self):
        u"""
        Перенести предметы из одного b2 мира в другой
        """
        pass
