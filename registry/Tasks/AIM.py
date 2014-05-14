# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


class Aim(Task):

    def __init__(self, master,  weapon, target):
        Task.__init__(self, master)
        self.weapon = weapon
        self.target = target

    def __call__(self, dt):
        vx = self.target.position[0] - self.master.position[0]
        vy = self.target.position[1] - self.master.position[1]
        #print "POSITION", self.target.position[0], self.target.position[1]
        dx = con.LEFT if vx < 0 else con.RIGHT
        dy = con.DOWN if vy < 0 else con.UP
        v = eu.Vector2(vx, vy)
        v = (v/abs(v))*consts['tile_size']
        pos = self.master.position
        #print "START", pos
        while not self.target.cshape.touches_point(pos[0], pos[1]):
            cell = self.environment.get_at_pixel(pos[0], pos[1])
            if cell.get('right') and dx is con.LEFT or cell.get('left') and dx is con.RIGHT or\
                            cell.get('top') and dy is con.DOWN or cell.get('bottom') and dy is con.UP:
                return COMPLETE
            pos += v
            #print pos
        #print self.master, self.weapon, v
        self.master.push_task(Shoot(self.master, self.weapon, self.target))
        return COMPLETE