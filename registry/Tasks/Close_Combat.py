# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
import random as rnd

from ..utility import COMPLETE
from task import *
from .Random_Attack import *
from .Turn import *
from .Walk import *
from .Move_Back import *


class Close_Combat(Task):

    def __init__(self, master, brain, target):
        Task.__init__(self, master)
        self.brain = brain
        self.target = target

    def __call__(self, dt):
        #print "ololo"
        dst = abs(self.target.cshape.center.x - self.master.cshape.center.x)
        if dst <= self.brain.eff_dst and self.target.fight_group > 0:
            d = dst/abs(dst) if abs(dst) != 0 else 0
            if d != self.master.direction:
                self.master.push_inst_task(Turn(self.master, 11))
            hand = self.master.choose_free_hand()
            self.master.push_inst_task(Random_Attack(self.master, hand, self.target))
            mv = rnd.random()
            if mv < 0.05:
                self.master.push_inst_task(Walk(self.master, 0.1))
            elif mv < 0.01:
                self.master.push_inst_task(Move_Back(self.master, 0.1))
        else:
            return COMPLETE