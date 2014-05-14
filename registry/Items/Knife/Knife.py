# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Knife(items.Usage_Item):

    size = items.SMALL

    def __init__(self):
        img = consts['img']['knife']
        first_usage = usages.Chop([onh.damage(1)])
        second_usage = usages.Throw([onh.damage(1)])
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(1000)])