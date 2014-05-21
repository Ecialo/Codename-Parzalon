# -*- coding: utf-8 -*-
from .. import bodies
from pyglet.resource import image
Body = bodies.Body
from ...bodypart import *
from ...Bodyparts import Head
from ...Bodyparts import Chest
from ...Bodyparts import Legs
__author__ = 'Ecialo'


class Human(Body):

    anim = {'walk': image("walk"),
            'stand': image("stand"),
            'jump': image("stand"),
            'sit': image("sit")}

    parts_pos = {'walk': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 57))],
                 'stand': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 57))],
                 'jump': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 57))],
                 'sit': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 17))]}
    img = anim['stand']
    base_speed = 7

    def __init__(self, master):
        Body.__init__(self, master, [Chest, Head, Legs], 'Human')
        self.make_animation(self.anim, 'Human')