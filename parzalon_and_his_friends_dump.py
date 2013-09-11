# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
__author__ = "Ecialo"

import pyglet
from pyglet.window import key
from pyglet.window import mouse

import cocos
from cocos import collision_model as cm
from cocos import actions as ac
from cocos import euclid as eu
from cocos import layer
from cocos.director import director

import geometry as gm



consts = {'window': {'width': 800,
                     'height': 600,
                     'vsync': True,
                     'resizable': True},
          'bindings': {'left': key.A,
                       'right': key.D},
          'color': {'white': (255, 255, 255, 255)},
          'img': {'human': pyglet.resource.image('chelovek.jpg')},
          'params': {'human': {'speed': 200}},
          'parry_cos_disp': 0.5
         }



class Brain(ac.Action):
    
    def step(self, dt):
        self.sensing()
        self.activity(dt)
        
    def sensing(self):
        pass
    
    def activity(self, dt):
        pass
    

class Controller(Brain):
    
    bind = consts['bindings']
    
    def start(self):
        self.key = self.target.get_ancestor(cocos.layer.Layer).loc_key_handler
        self.mouse = self.target.get_ancestor(cocos.layer.Layer).loc_mouse_handler
    
    def activity(self, dt):
        dx = self.key[self.bind['right']] - self.key[self.bind['left']]
        dy = 0
        ndx = dx * dt * self.target.body.speed 
        ndy = dy
        #print self.key
        self.target.move(ndx, ndy)
        
        if self.mouse[mouse.LEFT] and self.target.actual_hit is None:
            self.target.weapon.do_hit(self.mouse['pos'])
        elif self.mouse[mouse.LEFT] and self.target.actual_hit is not None:
            self.target.weapon.aim(self.mouse['pos'])
        elif not self.mouse[mouse.LEFT] and self.target.actual_hit is not None:
            self.target.weapon.perform()
            self.target.finish_hit()
        else: 
            pass


class Dummy(Brain):
    
    def start(self):
        pass



def shape_to_cshape(shape):
    if isinstance(shape, gm.Rectangle):
        return cm.AARectShape(shape.pc, shape.h_width, shape.h_height)
    else:
        print shape.p.y, shape.v
        c = shape.p + shape.v/2
        return cm.AARectShape(c, abs(shape.v.x/2), abs(shape.v.y/2))


class Hit():
    
    def __init__(self, master, shape, on_hit_effects, on_parry_effects):
        self.shape = shape
        self.cshape = shape_to_cshape(shape)
        self.master = master
        self.on_hit_effects = on_hit_effects
        self.on_parry_effects = on_parry_effects
    
    def take_hit(self, other):
        pass
    
    def finish(self):
        self.master.finish_hit()
    
    def move(self, dx, dy):
        pass
    
    def aim(self, pos):
        pass
    
    def perform(self):
        pass


def cross_line_angle(line1, line2):
    if line1.intersect(line2) is not None:
        v1, v2 = line1.v, line2.v
        return abs(v1.dot(v2)/(v1.magnitude() * v2.magnitude()))
    else:
        return 1

class Slash(Hit, cocos.draw.Line):
    
    cross_cos = consts['parry_cos_disp']
    
    def __init__(self, master, stp, vec, length, effects):
        Hit.__init__(self, master, gm.LineSegment2(stp, vec), effects, [])
        cocos.draw.Line.__init__(self, stp, stp + vec, (0, 255, 0))
        self.length = length
    
    def take_hit(self, other):
        if isinstance(other, Slash):
            cos = cross_line_angle(self.shape, other.shape)
            if cos < self.cross_cos:
                pass
        else:
            pass
    
    def move(self, dx, dy):
        v = eu.Vector2(dx, dy)
        self.cshape.center += v
        self.start += v
    
    def aim(self, pos):
        self.end = self.start + pos.normalize() * self.length
        
    def perform(self):
        self.v = self.end - self.start


def create_weapon_slash(master, length, effects):
    class A(Slash):
        
        def __init__(self, stp, vec):
            super(A, self).__init__(master, stp, vec, length, effects)
    return A

def interval_proection(point, interval):
    if interval[0] <= point < interval[1]:
        return point
    elif point < interval[0]:
        return interval[0]
    else:
        return interval[1]

class Weapon(pyglet.event.EventDispatcher):
    
    def __init__(self, master, create_weapon_hit_type, size, effects):
        self.master = master
        self.hit_type = create_weapon_hit_type(master, size, effects)
        self.start_lift = (-master.body.img.height, master.body.img.height)
        self.start_luft = (-master.body.img.width, master.body.img.width)
    
    def do_hit(self, stp):
        stpv = self.master.from_global_to_self(eu.Vector2(*stp))
        x = interval_proection(stpv.x, self.start_luft)
        y = interval_proection(stpv.y, self.start_lift)
        start = self.master.from_self_to_global(gm.Point2(x, y))
        #print start
        vec = stp - start
        start = gm.Point2(start.x, start.y)
        #print start
        self.dispatch_event('do_hit', self.hit_type(start, vec))
    
    def aim(self, pos):
        self.master.actual_hit.aim(pos)
    
    def perform(self):
        self.master.actual_hit.perform()
        self.dispatch_event('hit_performed', self.master.actual_hit)
    
    def finish_hit(self):
        self.dispatch_event('remove_hit', self.master.actual_hit)
        self.master.actual_hit = None
    
Weapon.register_event_type('do_hit')
Weapon.register_event_type('hit_performed')
Weapon.register_event_type('remove_hit')


class Sword(Weapon):
    
    def __init__(self, master):
        hit_type = create_weapon_slash
        length = 8.0
        eff = []
        super(Sword, self).__init__(master, hit_type, length, eff)


class Body_Part():
    
    def __init__(self, master, shape, health, armor):
        self.master = master
        self.shape = shape
        self.attachment = []
        
        self.out_effects = []
        
        self.health = health
        self.armor = armor
        
    def remove(self):
        for eff in self.out_effects:
            eff(self.master)
        self.master.body_parts.remove(self)
    
    def take_hit(self, hit):
        actual_hit_zone = self.shape.intersect(hit.shape)
        if actual_hit_zone is not None:
            if isinstance(hit.shape, gm.Line2):
                if isinstance(actual_hit_zone, gm.Point2):
                    pass
                else:
                    pass
            else:
                if isinstance(actual_hit_zone, gm.Rectangle):
                    pass
                else:
                    pass




class Body():
    
    img = None
    base_speed = 0
    
    def __init__(self, master, body_parts):
        self.master = master
        self.speed = self.base_speed
        self.body_parts = body_parts
    
    def take_hit(self, hit):
        pass

class Human(Body):
    
    img = consts['img']['human']
    base_speed = consts['params']['human']['speed']
    
    def __init__(self, master):
        #super(Human, self).__init__(master, [])
        Body.__init__(self, master, [])




class Actor(cocos.sprite.Sprite):
    
    is_event_handler = True
    
    def __init__(self, body, weapon):
        self.body = body(self)
        super(Actor, self).__init__(self.body.img)
        self.cshape = cm.AARectShape(self.position, self.body.img.width/2,
                                                    self.body.img.height/2)
        self.weapon = weapon(self)
        
        self.actual_hit = None
        
    def move(self, dx, dy):
        vec = eu.Vector2(dx, dy)
        self.position += vec
        #print vec, self.cshape
        self.cshape.center += vec
        if self.actual_hit is not None:
            self.actual_hit.move(dx, dy)
    
    def do_hit(self, hit):
        self.actual_hit = hit
        
    def finish_hit(self):
        self.weapon.finish_hit()
        
    def from_self_to_global(self, pos):
        #print type(pos)(pos + self.position)
        return (pos + self.position)
    
    def from_global_to_self(self, pos):
        return pos - self.position



class Some_Kind_Of_Area(cocos.layer.Layer):
    
    is_event_handler = True
    
    def __init__(self):
        super(Some_Kind_Of_Area, self).__init__()
        
        self.loc_mouse_handler = {'pos': (0, 0),
                                  'd' : (0, 0),
                                  mouse.LEFT: False,
                                  mouse.RIGHT: False,
                                  mouse.MIDDLE: False}
        self.loc_key_handler = key.KeyStateHandler()
        director.window.push_handlers(self.loc_key_handler)
        
        self.collman = cm.CollisionManagerBruteForce()
        self.hits = []
        self.hero = Actor(Human, Sword)
        self.actors = []
        self.hero.move(200, 200)
        self.add(self.hero, z = 1)
        self.hero.do(Controller())
        
    def update(self):
        self.collman.clear()
        for hit in self.hits:
            self.collman.add(hit)
        #####
        for other in self.collman.iter_colliding(self.hero):
            pass
        self.collman.add(self.hero)
        for actor in self.actors:
            self.collman.add(actor)
        for obj1, obj2 in self.collman.iter_all_collisions():
            pass
            
    
    def do_hit(self, hit):
        self.add(hit, z = 0)
        
    def hit_performed(self, hit):
        self.hits.append(hit)
        
    def remove_hit(self, hit):
        self.hits.remove(hit)
        self.remove(hit)
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.loc_mouse_handler['pos'] = (x, y)
        self.loc_mouse_handler['d'] = (dx, dy)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifers):
        self.loc_mouse_handler['pos'] = (x, y)
        self.loc_mouse_handler['d'] = (dx, dy)
    
    def on_mouse_press(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = (x, y)
        self.loc_mouse_handler[buttons] = True
    
    def on_mouse_release(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = (x, y)
        self.loc_mouse_handler[buttons] = False



def create_level():
    scene = cocos.scene.Scene()
    scene.add(Some_Kind_Of_Area(), z = 0)
    scene.add(layer.ColorLayer(*consts['color']['white']), z = -1)
    return scene

def main():
    director.init(**consts['window'])
    lvl = create_level()
    director.run(lvl)

if __name__ == "__main__":
    main()

