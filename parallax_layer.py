# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from cocos.layer import Layer
from registry.window import window


class Parallax_Layer(Layer):

    def __init__(self, image, foreground):
        super(Parallax_Layer, self).__init__()

        hw = image.width
        hh = image.height
        hwm = foreground.width
        hhm = foreground.height
        self.kx = (hwm - hw)/hwm
        self.ky = (hhm - hh)/hhm