# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from task import Task
from registry.utility import COMPLETE

class Shoot(Task):

    def __init__(self, master, weapon, target):
        Task.__init__(self, master)
        self.weapon = weapon
        self.target = target

    def __call__(self, dt):
        hand = self.weapon
        start = self.master.position
        end = self.target.position
        self.master.use_hand(hand, [start], [], [end, True])
        return COMPLETE