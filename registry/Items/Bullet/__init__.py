# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from pyglet.image import load
from registry.utility import module_path_to_os_path
from item import Item


class Bullet(Item):

    img = load(module_path_to_os_path(__name__) + "bullet.png")

    def __init__(self):
        super(Bullet, self).__init__(self.img)