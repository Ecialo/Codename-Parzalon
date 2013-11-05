import consts as con
import pyglet
import cocos
from cocos import layer


class Inventory(layer.Layer):
    def __init__(self, helmet, first_weapon, second_weapon, master):
        super(Inventory, self).__init__()
        self.image = cocos.sprite.Sprite(pyglet.image.load('inventory.png'))
        self.image.position = (350, 300)
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
        self.first_weapon.position = (490, 330)
        self.second_weapon.position = (190, 330)
        self.add(self.image)
        self.add(self.first_weapon)
        self.add(self.second_weapon)

    def close(self):
        self.remove(self.image)
        self.remove(self.first_weapon)
        self.remove(self.second_weapon)
