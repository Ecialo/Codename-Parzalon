import consts as con


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
        print self.helmet
        print self.first_weapon
        print self.second_weapon


