import consts
from cocos import layer
from cocos.scene import Scene
from cocos import tiles
from cocos import sprite
import items
import cocos
import pyglet
empty = pyglet.image.SolidColorImagePattern((255, 255, 255, 255)).create_image(32, 32)

MAX_INVENTORY_SIZE = 5


class Bag(tiles.RectMapLayer):

    is_event_handler = True

    def __init__(self, master):
        super(Bag, self).__init__(-1, MAX_INVENTORY_SIZE, MAX_INVENTORY_SIZE,
                                  [[tiles.RectCell(i, j, 32, 32, {}, tiles.Tile(-1, {}, empty))
                                    for j in xrange(MAX_INVENTORY_SIZE)]
                                  for i in xrange(MAX_INVENTORY_SIZE)])
        self.master = master

    def put_item(self, item):
        print item
        for column in self.cells:
            for cell in column:
                #print cell.tile
                if cell.tile is None:
                    cell.tile = item.inventory_representation
                    #break
                    return


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
        self.bag.position = (400, 200)

        self.add(buddy)
        self.add(self.bag, z=1)

    def put_item(self, item):
        if item.size is items.SMALL:
            self.bag.put_item(item)
        else:
            self.change_item(item)

    def open(self):
        self.master.get_ancestor(Scene).add(self, z=5)
        for column in self.bag.cells:
            for cell in column:
                #print cell.tile
                pass

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


