# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from pyglet.image import load
from item import Usage_Item
from registry.item import SMALL
from registry.utility import module_path_to_os_path
from registry import BASE
Chop = BASE['Chop']
Throw = BASE['Throw']
damage = BASE['damage']
length = BASE['length']


class Knife(Usage_Item):

    size = SMALL
    img = load(module_path_to_os_path(__name__) + 'knife.png')

    def __init__(self):
        first_usage = Chop([damage(1)])
        second_usage = Throw([damage(1)])
        super(Knife, self).__init__(self.img, first_usage, second_usage, [length(1000)])