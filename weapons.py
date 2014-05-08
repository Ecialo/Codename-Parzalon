# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"

import items
import usages
import consts as con
import on_hit_effects as onh

consts = con.consts


class Sword(items.Usage_Item):

    def __init__(self):
        img = con.img['weapon']
        first_usage = usages.Chop([onh.damage(1), onh.knock_back(100)])
        second_usage = usages.Stab([onh.damage(7)])
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(100)])


class Knife(items.Usage_Item):

    size = items.SMALL

    def __init__(self):
        img = consts['img']['knife']
        first_usage = usages.Chop([onh.damage(1)])
        second_usage = usages.Throw([onh.damage(1)])
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(1000)])


class Musket(items.Usage_Item):

    size = items.SMALL

    def __init__(self):
        img = con.img['rifle']
        first_usage = usages.Stab([onh.damage(3)])
        second_usage = usages.Shoot([onh.damage(10)], con.img['bullet'])
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(100), items.fire_rate(1.0), items.ammo(10)])


class Hands(items.Usage_Item):

    def __init__(self):
        img = con.img['weapon']
        first_usage = usages.Punch([onh.damage(1)])
        items.Usage_Item.__init__(self, img, first_usage, None, [items.length(100)])