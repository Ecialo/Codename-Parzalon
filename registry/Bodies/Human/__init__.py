# -*- coding: utf-8 -*-
import os

from pyglet import image

from registry.utility import module_path_to_os_path
from body import Body
from registry.bodypart import *
from registry import BASE

Chest = BASE['Chest']
Head = BASE['Head']
Legs = BASE['Legs']
__author__ = 'Ecialo'

path = module_path_to_os_path(__name__)


class Human(Body):

    print os.listdir(path)
    anim = {'walk': image.load(path + "walk.png"),
            'stand': image.load(path + "stand.png"),
            'jump': image.load(path + "stand.png"),
            'sit': image.load(path + "sit.png")}

    parts_pos = {'walk': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 57))],
                 'stand': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 57))],
                 'jump': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 57))],
                 'sit': [(LEGS, (0, -77)), (CHEST, (0, 0)), (HEAD, (0, 17))]}
    img = anim['stand']
    base_speed = 7

    def __init__(self, master):
        Body.__init__(self, master, [Chest, Head, Legs], 'Human')
        self.make_animation(self.anim, 'Human', path)