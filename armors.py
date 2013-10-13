__author__ = 'Ecialo'
from cocos import euclid as eu

import items
from bodies import Body_Part
import consts as con
consts = con.consts


def armor_crash(armor):
    sl = armor.slot - con.ARMOR
    for body_part in armor.master.body_parts:
        if body_part.slot is sl:
            body_part.attached.destroy()
            print "Armor_destroy"
            print "Yes" if armor in armor.master.body_parts else "No"
            break


class Shell(Body_Part):

    def drop(self):
        #print 11111
        sl = self.slot - con.ARMOR
        for body_part in self.master.body_parts:
            if body_part.slot is sl:
                body_part.attached.drop()


class Armor(items.Item):

    def __init__(self, img, shell):
        items.Item.__init__(self, img)
        self.shell = shell

    def destroy(self):
        self.master.attached = None
        self.master = None

    def drop(self):
        #print 2222222
        self.master.attached = None
        items.Item.drop(self)


class Helmet_Shell(Shell):

    max_health = 1
    max_armor = 10
    slot = con.ARMOR + con.HEAD

    def __init__(self):
        Shell.__init__(self, None, eu.Vector2(0, 57), 17, 22, 1, 1,
                       [armor_crash])


class Helmet(Armor):

    slot = con.HEAD

    def __init__(self):
        Armor.__init__(self, consts['img']['helmet'], Helmet_Shell())