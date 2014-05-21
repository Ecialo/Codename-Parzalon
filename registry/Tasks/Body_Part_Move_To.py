# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from ..utility import COMPLETE
from .Task import Task

class Body_Part_Move_To(Task):

    def __init__(self, master, pos, slot):
        Task.__init__(self, master)
        self.pos = pos
        self.slot = slot

    def __call__(self, dt):
        for body_part in self.master.body_parts:
            if body_part.slot is self.slot:
                body_part.set_pos(self.pos)
                return COMPLETE