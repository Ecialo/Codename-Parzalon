# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from  task import Task
import random as rnd
from registry.utility import COMPLETE
import cocos.euclid as eu
from registry.group import CHOP

class Random_Attack(Task):

    def __init__(self, master, weapon, target):
        Task.__init__(self, master)
        self.target = target
        self.weapon = weapon

    def __call__(self, dt):
        hand = self.weapon
        target = self.target
        if rnd.random() < 0.05 or hand is None or not hand.available:
            return COMPLETE
        dire = target.position[0] - self.master.position[0]
        dire = dire/abs(dire) if dire != 0 else 0
        h = rnd.randint(-self.master.height/2, self.master.height/2)
        h += self.master.position[1]
        x = self.master.position[0] + self.master.width*dire
        targ_x = target.position[0] + rnd.randint(-target.width/2, target.width/2)
        targ_y = target.position[1] + rnd.randint(-target.height/2, target.height/2)
        start = eu.Vector2(x, h)
        end = (targ_x, targ_y)
        self.master.use_hand(hand, [start, CHOP], [end])
        return COMPLETE