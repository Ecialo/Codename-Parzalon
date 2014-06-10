# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from task import Task
from registry.utility import COMPLETE
import random as rnd
from registry.something import MASTERY


class Parry(Task):

    def __init__(self, master,  weapon, target):
        Task.__init__(self, master)
        self.target = target
        self.weapon = weapon

    def __call__(self, dt):
        # hit = self.target
        # hand = self.weapon
        # if self.target.fight_group < 0 or rnd.random() < MASTERY or hand is None or \
        #         not hand.available:
        #     #print 13
        #     return COMPLETE
        # print "\nparry", hit, "\n"
        # h = hit.start.y
        # dire = hit.start.x - self.master.position[0]
        # dire = dire/abs(dire) if dire != 0 else 0
        # v = cross_hit_trace(hit)
        # x = self.master.position[0] + self.master.width*dire
        # start = eu.Vector2(x, h)
        # self.master.use_hand(hand, [start, con.CHOP], [start+v])
        return COMPLETE