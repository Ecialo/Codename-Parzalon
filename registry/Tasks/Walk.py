# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Walk(Task):

    def __call__(self, dt):
        Animate(self.master, 'walk')
        self.master.walk(self.master.direction)
        if self.master.wall & (con.LEFT | con.RIGHT):
                    self.master.push_inst_task(Jump(self.master))
        return Task.__call__(self, dt)