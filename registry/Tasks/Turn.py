# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Turn(Task):

    def __call__(self, dt):
        self.master.turn()
        #self.master.direction = -self.master.direction
        return COMPLETE