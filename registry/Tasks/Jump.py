# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from task import Task

class Jump(Task):

    def __call__(self, dt):
        print self
        Animate(self.master, 'jump')
        self.master.jump()
        return COMPLETE