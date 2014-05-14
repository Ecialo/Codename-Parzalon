# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Sword(items.Usage_Item):

    def __init__(self):
        img = con.img['weapon']
        first_usage = usages.Chop([onh.damage(1), onh.knock_back(100)])
        second_usage = usages.Stab([onh.damage(7)])
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(100)]