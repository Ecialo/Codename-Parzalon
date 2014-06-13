# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


def Animate(master, name):
    if master.state != name:
        master.state = name
        master.image = master.body.anim[name]