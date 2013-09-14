# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
__author__="Ecialo"
__date__ ="$24.08.2013 12:53:14$"

from cocos import euclid as eu
import geometry as gm
import consts as con
import effects as eff
import box

consts = con.consts


def death(body_part):
    body_part.master.destroy()


class Body_Part():
    
    max_health = 10
    max_armor = 10
    
    def __init__(self, master, center, h_height, h_width, stab_priority, chop_priority):
        self.master = master
        
        self.health = self.max_health
        self.armor = self.max_armor
        
        self.on_destroy_effects = [death]
        
        # Center relatively body
        p = gm.Point2(center.x - h_width, center.y - h_height)
        v = eu.Vector2(h_width * 2, h_height * 2)
        self.shape = gm.Rectangle(p, v)
        self.stab_priority = stab_priority
        self.chop_priority = chop_priority
    
    def take_hit(self, hit):
        for effect in hit.effects:
            effect(self)
        if self.health <= 0:
            self.destroy()
        print self.health, self.armor
        
    def destroy(self):
        self.master.body_parts.remove(self)
        for effect in self.on_destroy_effects:
                effect(self)
        

class Chest(Body_Part):
    
    def __init__(self, master):
        #super(Chest, self).__init__(master, eu.Vector2(0.0, 0.0), 45.0, 111.0, 1, 1)
        Body_Part.__init__(self, master, eu.Vector2(0, 0), 40, 25, 1, 1)


class Head(Body_Part):
    def __init__(self, master):
        #super(Chest, self).__init__(master, eu.Vector2(0.0, 0.0), 45.0, 111.0, 1, 1)
        Body_Part.__init__(self, master, eu.Vector2(0, 57), 15, 20, 2, 2)



class Legs(Body_Part):
    def __init__(self, master):
        #super(Chest, self).__init__(master, eu.Vector2(0.0, 0.0), 45.0, 111.0, 1, 1)
        Body_Part.__init__(self,master, eu.Vector2(0, -77), 33, 25, 1, 1)


class Body():
    
    img = None
    base_speed = 0
    
    def __init__(self, master, body_parts):
        self.master = master
        self.speed = self.base_speed
        self.body_parts = body_parts
        
    def destroy(self):
        self.master.destroy()
    
    def take_hit(self, hit):
        #Overlaps cshapes is not guarantee of successful attack
        #Need to compare shapes and traces
        x, y = hit.end.x, hit.end.y
        if not self.master.touches_point(x, y):
            return #False
        inner_p = self.master.from_global_to_self(hit.trace.p)
        inner_trace = gm.LineSegment2(gm.Point2(inner_p.x, inner_p.y), hit.trace.v)
        self.body_parts.sort(lambda x, y: y.chop_priority - x.chop_priority)
        for part in self.body_parts:
            if part.shape.intersect(inner_trace) is not None:
                p = gm.Point2(x, y)
                #print x, y
                eff.Blood().add_to_surface(p)
                part.take_hit(hit)
                return #True
        #return False

    def show_hitboxes(self):
        for bp in self.body_parts:
            self.master.add(box.Box(bp.shape, (255, 0, 0, 255)))
    
    

class Human(Body):
    
    img = consts['img']['human']
    base_speed = consts['params']['human']['speed']
    
    def __init__(self, master):
        #super(Human, self).__init__(master, [Chest(self)])
        Body.__init__(self, master, [Chest(self), Head(self), Legs(self)])

