import consts
from cocos import layer
import cocos
import pyglet


class Inventory(layer.Layer):

    is_event_handler = True

    def __init__(self, helmet, first_weapon, second_weapon, additional_weapon, master):
        super(Inventory, self).__init__()
        self.inv = {'helmet': helmet,
                    'first_weapon': first_weapon,
                    'second_weapon': second_weapon,
                    'additional_weapon': additional_weapon}
        self.master = master
        self.image = cocos.sprite.Sprite(pyglet.image.load('inventory.png'))
        self.image.position = (370, 300)

    def put_item(self, item):
        if item.slot != consts.HAND:
            self.inv['helmet'] = item
        elif not self.inv['first_weapon']:
            self.inv['first_weapon'] = item
        elif not self.inv['second_weapon']:
            self.inv['second_weapon'] = item
        else:
            self.inv['additional_weapon'] = item

    def get_item(self, item):
        if item.slot == consts.HAND:
            if not self.master.hands:
                self.master.hands.append(item)
                item.master = self.master
            elif len(self.master.hands) == 1:
                self.master.hands.append(item)
                item.master = self.master
            else:
                self.master.hands.append(item)
                item.master = self.master
        else:
            for body_part in self.master.body.body_parts:
                if body_part.slot is item.slot:
                    body_part.get_on(item)
                    break

    def open(self):
        self.add(self.image)
        self.inv['helmet'].position = (360, 480)
        self.inv['first_weapon'].position = (510, 350)
        self.inv['first_weapon'].rotation = 90
        if self.inv['second_weapon'].__class__.__name__ != 'Sword':
            self.inv['second_weapon'].position = (200, 500)
        else:
            self.inv['second_weapon'].rotation = 90
            self.inv['second_weapon'].position = (200, 350)
        self.inv['additional_weapon'].position = (150, 120)
        self.add(self.inv['helmet'], z=5)
        if self.master.hands[0]:
            self.add(self.inv['first_weapon'], z=5)
        if self.master.hands[1]:
            self.add(self.inv['second_weapon'], z=5)
        if self.master.hands[2]:
            self.add(self.inv['additional_weapon'], z=5)

    def close(self):
        self.remove(self.image)
        self.remove(self.inv['helmet'])
        if self.master.hands[0]:
            self.remove(self.inv['first_weapon'])
        if self.master.hands[1]:
            self.remove(self.inv['second_weapon'])
        if self.master.hands[2]:
            self.remove(self.inv['additional_weapon'])

    def change_weapon(self):
        swap = self.inv['second_weapon']
        self.inv['second_weapon'] = self.inv['additional_weapon']
        self.inv['additional_weapon'] = swap
        swap = self.master.hands[1]
        self.master.hands[1] = self.master.hands[2]
        self.master.hands[2] = swap


