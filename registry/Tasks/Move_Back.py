# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Move_Back(Task):

    def __call__(self, dt):
        Animate(self.master, 'walk')
        self.master.walk(-self.master.direction)
        return Task.__call__(self, dt)