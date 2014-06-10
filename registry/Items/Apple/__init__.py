# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from pyglet.image import load
from registry.utility import module_path_to_os_path
from item import Item


class Apple(Item):

    img = load(module_path_to_os_path(__name__) + "apple.jpg")

    def __init__(self):
        super(Apple, self).__init__(self.img)