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

        """
        Body Part receive all effects from Hit
        and apply them to self
        """

        for effect in hit.effects:
            effect(self)
        if self.health <= 0:
            self.destroy()
        print self.health, self.armor
        
    def destroy(self):

        """
        Remove self and apply some effects
        """

        self.master.body_parts.remove(self)
        for effect in self.on_destroy_effects:
                effect(self)
        

class Chest(Body_Part):
    
    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, 0), 40, 25, 1, 1)


class Head(Body_Part):
    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, 57), 15, 20, 2, 2)



class Legs(Body_Part):
    def __init__(self, master):
        Body_Part.__init__(self,master, eu.Vector2(0, -77), 33, 25, 1, 1)


class Body():
    
    img = None
    base_speed = 0
    
    def __init__(self, master, body_parts):
        self.master = master
        self.speed = self.base_speed
        self.body_parts = body_parts
        
    def destroy(self):

        """
        Destroy Body's master
        """

        self.master.destroy()
    
    def take_hit(self, hit):

        """
        1)Check is Hit hit any part of whole body
        2)If yes then recalculate coords of Hit to self base
        3)Sort Body Parts with priority whats depend from Hit type
        4)Check is first priority part intersects with Hit
        5)If yes take hit else get next and try again until Body Parts over
        """

        #Overlaps cshapes is not guarantee of successful attack
        #Need to compare shapes and traces
        if hit.base_fight_group is self.master.fight_group:
            return
        x, y = hit.end.x, hit.end.y
        if not self.master.touches_point(x, y):
            return
        inner_p = self.master.from_global_to_self(hit.trace.p)
        inner_end_p = self.master.from_global_to_self(hit.trace.p + hit.trace.v)
        inner_p = gm.Point2(inner_p.x, inner_p.y)
        inner_end_p = gm.Point2(inner_end_p.x, inner_end_p.y)
        inner_trace = gm.LineSegment2(inner_p, inner_end_p)
        if hit.hit_pattern is con.CHOP:
            self.body_parts.sort(lambda a, b: a.chop_priority - b.chop_priority)
        else:
            self.body_parts.sort(lambda a, b: a.stab_priority - b.stab_priority)
        for part in self.body_parts:
            in_p = part.shape.intersect(inner_trace)
            if in_p is not None:
                p = gm.Point2(x, y)
                eff.Blood().add_to_surface(p)
                part.take_hit(hit)
                return

    def show_hitboxes(self):

        """
        Draw hitboxes of all Body Parts.
        """

        for bp in self.body_parts:
            self.master.add(box.Box(bp.shape, (255, 0, 0, 255)))
    
    

class Human(Body):
    
    img = consts['img']['human']
    base_speed = consts['params']['human']['speed']
    
    def __init__(self, master):
        Body.__init__(self, master, [Chest(self), Head(self), Legs(self)])

