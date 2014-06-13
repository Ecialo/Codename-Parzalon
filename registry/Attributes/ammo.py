# -*- coding: utf-8 -*-
__author__ = 'ecialo'


def ammo(value):
    def add_ammo(master):
        master.max_ammo = value
        master.ammo = value
    return add_ammo