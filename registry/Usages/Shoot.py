# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Shoot(Usage):

    def __init__(self, effects, bullet_image):
        self.bullet_image = bullet_image
        self.effects = effects

    # def start_use(self, *args):
    #     print 99999999999
    #     self.master.available = False

    def end_use(self, *args):
        if self.master.ammo:
            print 2312312321321312321
            end_point = eu.Vector2(*args[0])
            v = end_point - self.owner.cshape.center
            hit_zone = hit.Missile(self, self.bullet_image, v, 300, self.owner.position, con.LINE)
            self.actual_hit = hit_zone
            self.master.dispatch_event('on_launch_missile', hit_zone)
            hit_zone.show_hitboxes()
            self.master.on_use = False
            self.master.ammo -= 1
            print self.master.ammo
            if self.master.ammo > 0:
                self.master.available = False
                self.master.cur_reload = self.master.reload_time

    def destroy_missile(self, missile):
        self.master.dispatch_event('on_remove_missile', missile)