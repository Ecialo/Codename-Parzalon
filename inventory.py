import consts as con
import pyglet
import cocos
from cocos import layer


class Inventory():
    def __init__(self, helmet, first_weapon, second_weapon, master):
        self.helmet = helmet
        self.first_weapon = first_weapon
        self.second_weapon = second_weapon
        self.master = master

    def put_item(self, item):
        if item.slot != con.HAND:
            self.helmet = item
        elif not self.first_weapon:
            self.first_weapon = item
        else:
            self.second_weapon = item

    def get_item(self, item):
        if item.slot == con.HAND:
            self.master.hands.append(item)
            item.master = self.master
        else:
            for body_part in self.master.body.body_parts:
                if body_part.slot is item.slot:
                    body_part.get_on(item)
                    break

    def open(self):
        print self.first_weapon.image
        print self.second_weapon.image

    def close(self):
        pass


class InventoryLayer(layer.Layer):
    def __init__(self):
        super(InventoryLayer, self).__init__()
        self.image = cocos.sprite.Sprite(pyglet.image.load('inventory.png'))
        self.image.position = (350, 300)
        self.weapon = cocos.sprite.Sprite(pyglet.image.load('sword.png'))
        self.weapon.position = (350, 300)

    def open(self):
        self.add(self.image)
        self.add(self.weapon)


    def close(self):
        self.remove(self.image)
