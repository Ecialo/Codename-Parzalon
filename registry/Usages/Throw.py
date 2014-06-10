# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from usage import Usage
import cocos.euclid as eu
import hit


class Throw(Usage):

    def __init__(self, effects):
        self.effects = effects
        self.actual_hit = None

    def start_use(self, *args):
        pass

    def continue_use(self, *args):
        pass

    def end_use(self, *args):
        end_point = eu.Vector2(*args[0])
        v = end_point - self.owner.cshape.center
        hit_zone = hit.Missile(self, self.master.image, v, 300, self.owner.position, con.LINE)
        self.actual_hit = hit_zone
        self.master.dispatch_event('on_launch_missile', hit_zone)
        #hit_zone.show_hitboxes()
        #self.owner.hands.remove(self.master)
        self.owner.hands.remove(self.master)
        self.master.on_use = False
        self.master.available = True
        self.master.length -= 1

    def destroy_missile(self, missile):
        self.master.dispatch_event('on_remove_missile', missile)