import consts as con
from cocos import layer


class Inventory(layer.Layer):

    is_event_handler = True

    def __init__(self, helmet, first_weapon, second_weapon, master):
        super(Inventory, self).__init__()
        self.inv = {'helmet': helmet,
                    'first_weapon': first_weapon,
                    'second_weapon': second_weapon}
        self.master = master
        print master

    def put_item(self, item):
        if item.slot != con.HAND:
            self.inv['helmet'] = item
        elif not self.inv['first_weapon']:
            self.inv['first_weapon'] = item
        else:
            self.inv['second_weapon'] = item

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
        print 'open'
        self.inv['helmet'].position = (40, 40)
        self.inv['first_weapon'].position = (110, 40)
        self.inv['second_weapon'].position = (190, 40)
        for i in self.inv:
            self.add(self.inv[i], z=5)

    def close(self):
        for i in self.inv:
            if self.inv[i]:
                self.remove(self.inv[i])

