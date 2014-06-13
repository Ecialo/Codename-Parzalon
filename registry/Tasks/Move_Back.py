# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from task import Task
from .Animate import *

class Move_Back(Task):

    def __call__(self, dt):
        Animate(self.master, 'walk')
        self.master.move(-self.master.direction)
        return Task.__call__(self, dt)