# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"
__date__ = "$24.08.2013 12:52:23$"

import random as rnd

from pyglet.window import mouse

from cocos import actions as ac
from cocos import euclid as eu
from cocos import layer

import consts as con

consts = con.consts

def _set_rec(self, val):
    self.master.recovery = val

class Brain(ac.Action):
    
    master = property(lambda self: self.target)
    recovery = property(lambda self: self.master.recovery, _set_rec)
    
    def start(self):
        self.master.fight_group = self.fight_group
        #self.tilemap = self.master.get_ancestor(cocos.layer.ScrollableLayer).force_ground
    
    def step(self, dt):
        self.sensing()
        self.activity(dt)
        
    def sensing(self):
        pass
    
    def activity(self, dt):
        pass

class Controller(Brain):
    
    bind = consts['bindings']
    fight_group = consts['group']['hero']
    
    def start(self):
        Brain.start(self)
        self.key = \
         self.master.get_ancestor(layer.ScrollableLayer).loc_key_handler
         
        self.mouse = \
         self.master.get_ancestor(layer.ScrollableLayer).loc_mouse_handler
         
        self.scroller = \
         self.master.get_ancestor(layer.ScrollableLayer).scroller
    
    def activity(self, dt):
        #print self.target.on_ground
        hor_dir = self.key[self.bind['right']] - self.key[self.bind['left']]
        if self.key[self.bind['jump']] and self.master.on_ground:
            self.master.jump()
        #print self.key
        #if abs(ndx) > 0.0 and ndy > 0.0:
        self.master.walk(hor_dir, dt)
        
        if self.mouse[mouse.LEFT] and self.master.actual_hit is None:
            self.master.start_attack(self.mouse['pos'])
        elif self.mouse[mouse.LEFT] and self.master.actual_hit is not None and not self.master.attack_perform:
            self.master.aim(self.mouse['pos'])
        elif not self.mouse[mouse.LEFT] and self.master.actual_hit is not None\
             and not self.master.attack_perform:
            self.master.perform()
        else: 
            pass
        cx, cy = self.master.position
        #print cx, cy
        self.scroller.set_focus(cx, cy)


class Dummy(Brain):
    
    fight_group = consts['group']['opponent']
    
    def activity(self, dt):
        self.master.walk(0, dt)
            
        if self.master.actual_hit is None:
            #print "Ololo"
            self.master.start_attack(self.master.position -
                                     eu.Vector2(self.master.width, 0.0))
            self.master.aim(self.master.position + eu.Vector2(-50.0, 50.0))
            self.master.perform()


class Primitive_AI(Brain):
    
    fight_group = consts['group']['opponent']
    mastery = consts['params']['primitive']['mastery']
    range_of_vision = consts['params']['primitive']['range_of_vision']
    closest = consts['params']['primitive']['closest']
    
    def start(self):
        Brain.start(self)
        self.vision = \
                self.master.get_ancestor(layer.ScrollableLayer).collman
        self.visible_actors_wd = []
        self.visible_hits_wd = []

        self.prev_move = 0
        self.mt = 0.0
        
    def sensing(self):
        self.clear_vision()
        for obj_wd in self.vision.objs_near_wdistance(self.master, self.range_of_vision):
            if obj_wd[0].fight_group < consts['slash_fight_group']:
                self.visible_actors_wd.append(obj_wd)
            else:
                self.visible_hits_wd.append(obj_wd)
    
    def activity(self, dt):
        #print self.master.cshape.center
        #if self.master.wall & (LEFT | RIGHT):
        #    print 123
        if self.recovery > 0:
            self.recovery -= dt
        opp_wd = None
        for obj_wd in self.visible_actors_wd:
            if obj_wd[0].fight_group == consts['group']['hero']:
                opp_wd = obj_wd
                break
        #Saw enemy
        if opp_wd is not None:
            opp = opp_wd[0]
            wd = opp_wd[1]
            d = opp.cshape.center.x - self.master.cshape.center.x
            dir = d/abs(d) if d != 0 else 0
            #Too far for attack.Come closer.
            if wd > self.master.weapon.length * consts['effective_dst']:
                self.mt = 0.0
                self.prev_move = 0
                self.master.walk(dir, dt)
                #Brick on way. Must jump over
                if self.master.wall & (con.LEFT | con.RIGHT):
                    self.master.jump()
                #Parry if any danger
                for hit_wd in self.visible_hits_wd:
                    if self.is_in_touch(hit_wd[0]):
                        if self.is_enemy(hit_wd[0]) and rnd.random() < self.mastery:
                            #print "!!!"
                            self.parry(hit_wd[0])
            #Close enough for attack. Dance across
            else:
                if self.mt > 0:
                    self.mt -= dt
                    self.master.walk(self.prev_move, dt)
                else:
                    mv = rnd.random()
                    if wd > self.closest and mv < 0.05:
                        self.prev_move = dir
                        self.mt = 0.1
                        self.master.walk(dir, dt)
                    elif mv < 0.01:
                        self.prev_move = -dir
                        self.mt = 0.5
                        self.master.walk(-dir, dt)
                    else:
                        self.master.stay(dt)
                #Parry if any danger
                for hit_wd in self.visible_hits_wd:
                    if self.is_in_touch(hit_wd[0]):
                        if self.is_enemy(hit_wd[0]) and rnd.random() < self.mastery:
                            #print "!!!"
                            self.parry(hit_wd[0])
                            break
                #Die, my enemy!
                else:
                    if rnd.random() < 0.05:
                        #print "123"
                        self.random_attack(opp)
        else:
            self.master.stay(dt)

    def clear_vision(self):
        self.visible_actors_wd = []
        self.visible_hits_wd = []

    def cross_hit_trace(self, hit):
        v = hit.trace.v
        nv = v.cross()
        if v.x >= 0 and v.y < 0 or v.x < 0 and v.y < 0:
            return nv
        else:
            return -nv

    def is_enemy(self, other):
        if other.fight_group < 100:
            return self.master.fight_group == other.fight_group
        else:
            return self.master.fight_group == other.fight_group % consts['slash_fight_group']

    def is_in_touch(self, other):
        return self.master.cshape.overlaps(other.cshape)

    def parry(self, hit):
        if self.recovery > 0.0 or self.master.actual_hit is not None:
            return
        #print "parry"
        h = hit.start.y
        dire = hit.start.x - self.master.position[0]
        dire = dire/abs(dire) if dire != 0 else 0
        v = self.cross_hit_trace(hit)
        x = self.master.position[0] + self.master.width*dire
        start = eu.Vector2(x, h)
        self.master.attack(start, start + v)
        self.recovery = 0.05

    def random_attack(self, other):
        if self.recovery > 0.0 or self.master.actual_hit is not None:
            return
        dire = other.position[0] - self.master.position[0]
        dire = dire/abs(dire) if dire != 0 else 0
        h = rnd.randint(-self.master.height/2, self.master.height/2)
        h += self.master.position[1]
        x = self.master.position[0] + self.master.width*dire
        targ_x = other.position[0] + rnd.randint(-other.width/2, -other.width/2)
        targ_y = other.position[1] + rnd.randint(-other.height/2, -other.height/2)
        start = eu.Vector2(x, h)
        end = (targ_x, targ_y)
        self.master.attack(start, end)
        self.recovery = 0.05

if __name__ == "__main__":
    print "Hello World"
