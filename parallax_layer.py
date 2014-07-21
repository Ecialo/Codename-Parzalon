# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from cocos.sprite import Sprite
from registry.window import window
from registry.utility import clamp


class Parallax_Manager(object):

    def __init__(self):
        self.image = None
        self.kx = 1.0
        self.ky = 1.0
        self.map_half_width = 0.0
        self.map_half_height = 0.0
        self.clamp_x = None
        self.clamp_y = None
        print "MANAGER"

    def __set__(self, scroller, value):
        print "SSSSSS"
        if value is not None:
            location = scroller.get('background')
            hwm = (location.px_width - window['width'])/2
            hhm = (location.px_height - window['height'])/2
            hw = value.width/2
            hh = value.height/2
            print "Map"
            print hwm, hhm
            print "Back"
            print hw, hh

            self.image = Sprite(value)
            self.clamp_x = clamp(window['width']/2, location.px_width - window['width']/2)
            self.clamp_y = clamp(window['height']/2, location.px_height - window['height']/2)
            self.map_half_width = hwm
            self.map_half_height = hhm
            self.kx = (hwm - hw)/float(hwm)
            self.ky = (hhm - hh)/float(hhm)
        else:
            self.image = None

        # def __get__(self, instance, owner):
        #     print "GGGGGGGG"
        #     return self.image

    def set_position(self, fx, fy):
        if self.image is not None:
            cx = window['width']/2 - self.kx*(self.clamp_x(fx) - self.map_half_width)
            cy = window['height']/2 - self.ky*(self.clamp_y(fy) - self.map_half_height)
            self.image.position = (cx, cy)

    def __nonzero__(self):
        return bool(self.image)