# -*- coding: utf-8 -*-
__author__ = 'ecialo'

from cocos import sprite
from pyglet.graphics import OrderedGroup


class Sprite(sprite.Sprite):

    def set_batch(self, batch, groups=None, z=0):
        self.batch = batch
        if batch is None:
            self.group = None
        else:
            group = groups.get(z)
            if group is None:
                group = OrderedGroup(z)
                groups[z] = group
            self.group = group
        for childZ, child in self.children:
            child.set_batch(self.batch, groups, z + childZ)