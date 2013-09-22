# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"
__date__ = "$24.08.2013 12:52:47$"

import pyglet

#from cocos import collision_model as cm
from cocos import euclid as eu

#import geometry as gm
import consts as con
import on_hit_effects as on_h
import hits as hit

consts = con.consts


def interval_proection(point, interval):

    """
    Return point in interval closet to given
    """

    if interval[0] <= point < interval[1]:
        return point
    elif point < interval[0]:
        return interval[0]
    else:
        return interval[1]


class Hand(pyglet.event.EventDispatcher):

    def start_use(self, *args):
        pass

    def continue_use(self, *args):
        pass

    def end_use(self, *args):
        pass


class Weapon(Hand):
    
    def __init__(self, name, length, weight, effects, environment):
        super(Weapon, self).__init__()
        self.master = None

        self.name = name
        self.hit_type = hit.Slash
        self.length = length
        self.weight = weight

        self.chop_time = consts['test_slash_time']
        self.stab_time = consts['test_slash_time']
        
        self.effects = map(lambda eff: eff(self), effects)
        
        self.actual_hit = None
        self.attack_perform = False

        self.push_handlers(environment)
    
    def start_use(self, *args):
        """
        Create line what start from closest to start point possible place near Actor.
        """
        #Define start point of hit line on screen
        start_point, hit_pattern = args
        if isinstance(start_point, eu.Vector2):
            stp = start_point.copy()
        else:
            stp = eu.Vector2(*start_point)
        stp = self.master.from_global_to_self(stp)
        stp.x = stp.x/abs(stp.x) if stp.x != 0 else 0
        stp.x *= self.master.width/2
        stp.y = interval_proection(stp.y, (-self.master.height/2,
                                           self.master.height/2))
        stp = self.master.from_self_to_global(stp)
        #Define end point of hit line on screen
        vec = start_point - stp
        end = stp + vec.normalize()*self.length
        #Send line to holder in weapon for update end point and to screen for draw
        self.actual_hit = self.hit_type(stp, end, self, hit_pattern)
        self.dispatch_event('do_hit', self.actual_hit)
        
    def continue_use(self, *args):
        """
        Define new end point
        """
        end_point = args[0]
        start_point = self.actual_hit.start
        vec = end_point - start_point
        end = start_point + vec.normalize()*self.length
        self.actual_hit.end = end
        
    def end_use(self, *args):
        """
        Create full collidable obj from line and memor what attack is going on
        """
        self.attack_perform = True
        self.actual_hit.perform(self.chop_time)
        self.dispatch_event('hit_perform', self.actual_hit)
        
    def finish_hit(self):

        """
        Remove current Hit and complete attack
        """

        self.dispatch_event('remove_hit', self.actual_hit)
        self.attack_perform = False
        self.actual_hit = None
        
    def dearm(self):

        """
        Weapon now can't do anything
        """

        if self.attack_perform and self.actual_hit is not None:
            self.finish_hit()
        elif self.actual_hit is not None:
            self.actual_hit.kill()
        self.pop_handlers()
        
Weapon.register_event_type('do_hit')
Weapon.register_event_type('hit_perform')
Weapon.register_event_type('remove_hit')


class Standard_Weapon(Weapon):

    def __init__(self, environment):
        super(Standard_Weapon, self).__init__("wp",
                                              100,
                                              20,
                                              [on_h.damage(3), on_h.knock_back(100)],
                                              environment)
