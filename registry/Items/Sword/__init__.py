# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from pyglet.image import load
from registry.utility import module_path_to_os_path
from item import Usage_Item
from registry import BASE
Chop = BASE['Chop']
Stab = BASE['Stab']
length = BASE['length']
knock_back = BASE['knock_back']
damage = BASE['damage']


class Sword(Usage_Item):

    img = load(module_path_to_os_path(__name__) + "sword.png")

    def __init__(self):
        first_usage = Chop([damage(1), knock_back(100)])
        second_usage = Stab([damage(7)])
        super(Sword, self).__init__(self.img, first_usage, second_usage, [length(100)])