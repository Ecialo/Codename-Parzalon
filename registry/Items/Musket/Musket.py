# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Musket(items.Usage_Item):

    size = items.SMALL

    def __init__(self):
        img = con.img['rifle']
        first_usage = usages.Stab([onh.damage(3)])
        second_usage = usages.Shoot([onh.damage(10)], con.img['bullet'])
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(100), items.fire_rate(1.0), items.ammo(10)])