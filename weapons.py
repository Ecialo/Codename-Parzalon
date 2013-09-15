# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"
__date__ = "$24.08.2013 12:52:47$"

import pyglet

import cocos
from cocos import collision_model as cm
from cocos import euclid as eu

import geometry as gm
import consts as con
import effects as eff
import on_hit_effects as on_h

consts = con.consts

def printer(master):
    def sub_printer(body_part):
        print "Take THIS!"
    return sub_printer

def interval_proection(point, interval):
    if interval[0] <= point < interval[1]:
        return point
    elif point < interval[0]:
        return interval[0]
    else:
        return interval[1]


def shape_to_cshape(shape):
    if isinstance(shape, gm.Rectangle):
        return cm.AARectShape(shape.pc, shape.h_width, shape.h_height)
    else:
        #print shape.p.y, shape.v
        c = shape.p + shape.v/2
        return cm.AARectShape(c, abs(shape.v.x/2), abs(shape.v.y/2))


class Slash(cocos.draw.Line):
    
    
    def __init__(self, stp, endp, master):
        self.master = master
        self.fight_group = master.master.fight_group + consts['slash_fight_group']
        super(Slash, self).__init__(stp, endp, (0, 255, 0, 255))
        self._time_to_complete = 0.0
        self._color_c = 0.0
        self.cshape = None
        self.trace = None
    
    effects = property(lambda self: self.master.effects)
  
    def _change_time_to_complete(self, time):
        self._time_to_complete = time
        #print 111
        val = int(time * self._color_c)
        self.color = (255 - val, val, 0, 255)
    
    time_to_complete = property(lambda self: self._time_to_complete,
                                _change_time_to_complete)
                    
    def set_time_to_complete(self, time):
        self._time_to_complete = time
        self._color_c = 255.0 / time
    
    def perform(self, time):
        #Define geometry and time data
        v = self.end - self.start
        start = gm.Point2(self.start.x, self.start.y)
        self.trace = gm.LineSegment2(start, v)
        self.cshape = shape_to_cshape(self.trace)
        self.set_time_to_complete(time)
    
    def finish_hit(self):
        self.master.finish_hit()
        
    def _move(self, vec):
        self.start += vec
        self.end += vec
        if self.master.attack_perform:
            self.trace.p += vec
            self.cshape.center += vec
    
    def parry(self, other):
        p = self.trace.intersect(other.trace)
        if p is not None and self._cross_angle(other) <= consts['parry_cos_disp']:
            #print eff.Sparkles.add_to_surface
            #print p
            eff.Sparkles().add_to_surface(p)
            other.finish_hit()
            self.finish_hit()
    
    def _cross_angle(self, other):
        #Cos of angle between two hit lines
        v1 = self.trace.v
        v2 = other.trace.v
        angle = abs((v1.x * v2.x + v1.y * v2.y)/(abs(v1)*abs(v2)))
        #print angle
        return angle
        


class Weapon(pyglet.event.EventDispatcher):
    
    def __init__(self, master, length):
        super(Weapon, self).__init__()
        self.master = master
        self.hit_type = Slash
        self.length = length
        
        self.effects = [on_h.fab_damage(3)(self)]
        
        self.actual_hit = None
        self.attack_perform = False
    
    def start_attack(self, endp):
        #Define start point of hit line on screen
        if isinstance(endp, eu.Vector2):
            stp = endp.copy()
        else:
            stp = eu.Vector2(*endp)
        stp = self.master.from_global_to_self(stp)
        stp.x = stp.x/abs(stp.x) if stp.x != 0 else 0
        stp.x *= self.master.width/2
        stp.y = interval_proection(stp.y, (-self.master.height/2,
                                           self.master.height/2))
        stp = self.master.from_self_to_global(stp)
        #Define end point of hit line on screen
        vec = endp - stp
        end = stp + vec.normalize()*self.length
        #Send line to holder in weapon for update end point and to screen for draw
        self.actual_hit = self.hit_type(stp, end, self)
        self.dispatch_event('do_hit', self.actual_hit)
        
    def aim(self, endp):
        #Define new end point
        stp = self.actual_hit.start
        vec = endp - stp
        end = stp + vec.normalize()*self.length
        self.actual_hit.end = end
        
    def perform(self):
        self.attack_perform = True
        self.actual_hit.perform(consts['test_slash_time'])
        self.dispatch_event('hit_perform', self.actual_hit)
        
    def finish_hit(self):
        self.dispatch_event('remove_hit', self.actual_hit)
        self.attack_perform = False
        self.actual_hit = None
        
    def dearm(self):
        #self.dispatch_event('dearm_weapon', self)
        if self.attack_perform and self.actual_hit is not None:
            self.finish_hit()
        elif self.actual_hit is not None:
            self.actual_hit.kill()
        self.pop_handlers()
        
Weapon.register_event_type('do_hit')
Weapon.register_event_type('hit_perform')
Weapon.register_event_type('remove_hit')

if __name__ == "__main__":
    print "Hello World"
