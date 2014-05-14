# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Approaches(Task):

    def __init__(self, master, brain, target):
        Task.__init__(self, master)
        self.brain = brain
        self.target = target

    def __call__(self, dt):
        #print "Approach", self.target
        #print self.brain.task_manager.tasks
        Animate(self.master, 'walk')
        if self.target.fight_group > 0:
            dst = self.target.cshape.center.x - self.master.cshape.center.x
            d = dst/abs(dst) if abs(dst) != 0 else 0
            dst = abs(dst)
            #print dst
            if d != self.master.direction:
                self.master.push_inst_task(Turn(self.master))
            if dst <= self.brain.eff_dst:
                self.master.push_inst_task(Close_Combat(self.master, self.brain, self.target))
            else:
                self.master.walk(self.master.direction)
                if self.master.wall & (con.LEFT | con.RIGHT):
                    self.master.push_inst_task(Jump(self.master))
        else:
            self.master.push_task(Stand(self.master, 1))
            self.brain.observed_units.remove(self.target)
            #print "OLOLO"
            return COMPLETE