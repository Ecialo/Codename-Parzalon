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
          'parry_cos_disp': 0.5,
          'test_slash_time': 0.8
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
            self.target.start_attack(self.mouse['pos'])
        elif self.mouse[mouse.LEFT] and self.target.actual_hit is not None:
            self.target.aim(self.mouse['pos'])
        elif not self.mouse[mouse.LEFT] and self.target.actual_hit is not None\
             and not self.target.attack_perform:
            self.target.perform()
        else: 
            pass


class Dummy(Brain):
    
    def start(self):
        pass


def interval_proection(point, interval):
    if interval[0] <= point < interval[1]:
        return point
    elif point < interval[0]:
        return interval[0]
    else:
        return interval[1]


class Slash(cocos.draw.Line):
    
    def __init__(self, stp, endp):
        super(Slash, self).__init__(stp, endp, (0, 255, 0, 255))
        self._time_to_complete = 0.0
        self._color_c = 0.0
        self.cshape = None
        self.trace = None
        self.master = None
  
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
    
    def perform(self, master, time):
        #Define geometry and time data
        v = self.end - self.start
        start = gm.Point2(self.start.x, self.start.y)
        self.trace = gm.LineSegment2(start, v)
        self.set_time_to_complete(time)
        self.master = master
    
    def finish_hit(self):
        self.master.finish_hit()
        self.kill()


class Weapon(pyglet.event.EventDispatcher):
    
    def __init__(self, master, length):
        super(Weapon, self).__init__()
        self.master = master
        self.hit_type = Slash
        self.length = length
        
        self.actual_hit = None
        self.attack_perform = False
    
    def start_attack(self, endp):
        #Define start point of hit line on screen
        stp = eu.Vector2(*endp)
        stp = self.master.from_global_to_self(stp)
        stp.x = stp.x/abs(stp.x) * self.master.width/2
        stp.y = interval_proection(stp.y, (-self.master.height/2,
                                           self.master.height/2))
        stp = self.master.from_self_to_global(stp)
        #Define end point of hit line on screen
        vec = endp - stp
        endp = stp + vec.normalize()*self.length
        #Send line to holder in weapon for update end point and to screen for draw
        self.actual_hit = self.hit_type(stp, endp)
        self.dispatch_event('do_hit', self.actual_hit)
        
    def aim(self, endp):
        #Define new end point
        stp = self.actual_hit.start
        vec = endp - stp
        endp = stp + vec.normalize()*self.length
        self.actual_hit.end = endp
        
    def perform(self):
        self.attack_perform = True
        self.actual_hit.perform(self, consts['test_slash_time'])
        self.dispatch_event('hit_perform', self.actual_hit)
        
    def finish_hit(self):
        self.attack_perform = False
        self.actual_hit = None
        
Weapon.register_event_type('do_hit')
Weapon.register_event_type('hit_perform')
        
        

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
    
    def __init__(self, body):
        self.body = body(self)
        super(Actor, self).__init__(self.body.img)
        self.cshape = cm.AARectShape(self.position, self.body.img.width/2,
                                                    self.body.img.height/2)
        self.weapon = Weapon(self, 100)
    
    actual_hit = property(lambda self: self.weapon.actual_hit)
    heigth = property(lambda self: self.body.img.heigth)
    width = property(lambda self: self.body.img.width)
    attack_perform = property(lambda self: self.weapon.attack_perform)
        
    def move(self, dx, dy):
        vec = eu.Vector2(dx, dy)
        self.position += vec
        #print vec, self.cshape
        self.cshape.center += vec
        
    def start_attack(self, endp):
        self.weapon.start_attack(endp)
        
    def perform(self):
        self.weapon.perform()
    
    def aim(self, endp):
        self.weapon.aim(endp)
        
    def from_self_to_global(self, pos):
        #print type(pos)(pos + self.position)
        return pos + self.position
    
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
        self.hero = Actor(Human)
        self.hero.weapon.push_handlers(self)
        self.actors = []
        self.hero.move(200, 200)
        self.add(self.hero, z = 1)
        self.hero.do(Controller())
        
        #stp = eu.Vector2(100, 100)
        #endp = eu.Vector2(150, 150)
        
        #line = cocos.draw.Line(stp, endp, (0, 255, 0, 255))
        #self.add(line, z = 0)
        self.schedule(self.update)
        
    def update(self, dt):
        #self.collman.clear()
        #print 111
        for hit in self.hits:
            if hit.time_to_complete <= 0:
                self.remove_hit(hit)
            hit.time_to_complete = hit.time_to_complete - dt
        #    self.collman.add(hit)
        #####
        #for other in self.collman.iter_colliding(self.hero):
        #    pass
        #self.collman.add(self.hero)
        #for actor in self.actors:
        #    self.collman.add(actor)
        #for obj1, obj2 in self.collman.iter_all_collisions():
        #    pass
            
    
    def do_hit(self, hit):
        print "recive", hit
        self.add(hit, z = 1)
        
    def hit_perform(self, hit):
        print "performed", hit
        self.hits.append(hit)
        
    def remove_hit(self, hit):
        print "try to remove", hit
        self.hits.remove(hit)
        hit.finish_hit()
    
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

