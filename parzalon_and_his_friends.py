# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
__author__ = "Ecialo"

#import pyglet
from pyglet.window import key
from pyglet.window import mouse

import cocos
from cocos import collision_model as cm
#from cocos import actions as ac
from cocos import euclid as eu
#from cocos import layer
from cocos.director import director
from cocos import tiles
from cocos import layer

#import geometry as gm
import consts as con
import brains as br
import weapons as wp
import bodies as bd
import effects as eff

consts = con.consts

class Level_Collider(tiles.RectMapCollider):
    
    def collide_bottom(self, dy):
        self.wall |= con.DOWN
        self.on_ground = True
    
    def collide_top(self, dy):
        self.wall |= con.UP
        self.v_speed = 0
    
    def collide_left(self, dx):
        self.wall |= con.LEFT
    
    def collide_right(self, dy):
        self.wall |= con.RIGHT


class Actor(cocos.sprite.Sprite, Level_Collider):
    
    is_event_handler = True
    tilemap = None
    
    def __init__(self, body, w_len):
        self.fight_group = -1
        
        self.weapon = wp.Weapon(self, w_len)
        
        self.body = body(self)
        super(Actor, self).__init__(self.body.img)
        
        self.cshape = cm.AARectShape(eu.Vector2(*self.position), 
                                self.body.img.width/2, self.body.img.height/2)
        
        self.on_ground = False
        self.v_speed = 0
        self.wall = con.NO_TR

        self.recovery = 0.0  # Time before moment when acton can be controlled again
    
    actual_hit = property(lambda self: self.weapon.actual_hit)
    height = property(lambda self: self.body.img.height)
    width = property(lambda self: self.body.img.width)
    attack_perform = property(lambda self: self.weapon.attack_perform)
    
    def destroy(self):

        """
        Remove Actor from level
        """

        self.weapon.dearm()
        self.fight_group = -1
        self.kill()
        
    def walk(self, hor_dir, dt):

        """
        Move Actor in horizontal_direction with his body speed
        """

        dx = hor_dir * self.body.speed * dt
        self._move(dx, 0, dt)

    def stay(self, dt):

        """
        Do not move Actor
        """

        self._move(0, 0, dt)

    def attack(self, stp, enp):

        """
        Create Hit with Actor's Weapon. Hit start in start_point
        and end in end_point
        """

        self.start_attack(stp)
        self.aim(enp)
        self.perform()
        
    def _move(self, dx, ndy, dt):

        """
        Try to move Actor on dx, ndy with registrations all collisions
        with map.
        """

        dy = self.v_speed * dt if self.v_speed != 0 else 0
        dy += ndy
        self.on_ground = False
        self.wall = con.NO_TR
        orig = self.get_rect()
        last = self.get_rect()
        new = last.copy()
        new.x += dx
        self.collide_map(self.tilemap, last, new, dx, 0)
        last = new.copy()
        new.y += dy
        self.collide_map(self.tilemap, last, new, 0, dy)
        ndx, ndy = new.x - orig.x, new.y - orig.y
        if not self.on_ground:
            self.v_speed -= consts['gravity'] * dt
        else:
            self.v_speed = 0
        vec = eu.Vector2(int(ndx), int(ndy))
        self.position += vec
        self.cshape.center += vec
        if self.actual_hit is not None:
            self.actual_hit._move(vec)
    
    def jump(self):

        """
        Actor jump with his body jump speed.
        """

        self.v_speed = consts['params']['human']['jump_speed']
        self.on_ground = False
        
    def move_to(self, x, y):

        """
        Place Actor to x, y.
        """

        old = self.cshape.center.copy()
        vec = eu.Vector2(int(x), int(y))
        self.position = vec
        self.cshape.center = vec
        if self.actual_hit is not None:
            self.actual_hit._move(vec - old)
    
    def stand_off(self, other):

        """
        Push aside Actor from other collidable object
        """

        s_c = self.cshape.center
        o_c = other.cshape.center
        d = o_c - s_c
        l = self.width/2 + other.width/2
        dd = l - abs(d.x)
        if(d.x > 0):
            self._move(-dd, 0, 0)
        else:
            self._move(dd, 0, 0)

    def start_attack(self, start_point):

        """
        Set up start point of attack
        """

        self.weapon.start_attack(start_point)
        
    def perform(self):

        """
        Send current actual_hit to Level as collidable object
        for further checking of hit or miss
        """

        self.weapon.perform()
    
    def aim(self, end_point):

        """
        Set up end point of attack
        """

        self.weapon.aim(end_point)
        
    def take_hit(self, hit):

        """
        Check with every Body_Part is Hit hit or not.
        """

        self.body.take_hit(hit)
    
    def touches_point(self, x, y):

        """
        Checks whether the point lies on the actor
        """

        return self.cshape.touches_point(x, y)

    def show_hitboxes(self):

        """
        Show hitboxes of every Body_Part
        """

        self.body.show_hitboxes()
        
    def from_self_to_global(self, pos):

        """
        Recalculate position from Actors base to Level base
        """

        return pos + self.position
    
    def from_global_to_self(self, pos):

        """
        Recalculate position from Level base to Actors base
        """

        return pos - self.position


class Level_Layer(layer.ScrollableLayer):
    
    is_event_handler = True
    
    def __init__(self, scripts, force_ground, scroller):
        super(Level_Layer, self).__init__()
        
        #Controller
        self.loc_mouse_handler = {'pos': (0, 0),
                                  'd' : (0, 0),
                                  mouse.LEFT: False,
                                  mouse.RIGHT: False,
                                  mouse.MIDDLE: False}
        
        self.loc_key_handler = key.KeyStateHandler()
        director.window.push_handlers(self.loc_key_handler)
        
        #Tilemaps. Setup this on Actor.
        self.scroller = scroller
        self.force_ground = force_ground
        Actor.tilemap = force_ground #This bad

        #Setup layer for effects
        eff.Advanced_Emitter.surface = self #This bad
        
        #Collision managers. For static global and dynamic screen objects
        self.collman = cm.CollisionManagerBruteForce()
        self.static_collman = cm.CollisionManagerBruteForce()
        
        #Lists of dynamic objs
        self.hits = []
        self.actors = []
        
        #Append ground
        #self.add(force_ground, z = 1)
        
        #Append hero
        self.hero = Actor(bd.Human, 100)
        self.hero.weapon.push_handlers(self)
        #self.hero.move(200, 200)
        self.add(self.hero, z = 2)
        
        #Append opponent
        self.opponent = Actor(bd.Human, 100)
        self.opponent.weapon.push_handlers(self)
        #self.opponent.move(400, 200)
        self.add(self.opponent, z = 2)
        self.actors.append(self.opponent)
        
        #Move guys to location
        for sc in scripts:
            if sc.properties.has_key('player'):
                r = self.hero.get_rect()
                r.midbottom = sc.midbottom
                dx, dy = r.center
                self.hero.move_to(dx, dy)
            elif sc.properties.has_key('opponent'):
                r = self.opponent.get_rect()
                r.midbottom = sc.midbottom
                dx, dy = r.center
                self.opponent.move_to(dx, dy)
        
        #Set up brains
        #self.opponent.do(br.Primitive_AI())
        self.opponent.do(br.Dummy())
        self.hero.do(br.Controller())

        self.hero.show_hitboxes()
        self.opponent.show_hitboxes()
        
        #Run
        self.schedule(self.update)
        
    def _actor_kick_or_add(self, actor):

        """
        Remove Actor from self if he is dead
        """

        if actor.fight_group >= 0:
            self.collman.add(actor)
        else:
            self.actors.remove(actor)
        
    def update(self, dt):

        """
        1)Update Hits in dynamic collision manager and remove overdue objects
        2)Check all collisions between Hits
        3)Update Actors in collisions managers and remove dead Actors
        4)Check all collisions between Actors and immovable objects
        5)Check all collisions between all dynamic objects
        """

        #All collisions between movable objects calculate here
        self.collman.clear()
        for hit in self.hits:
            if hit.time_to_complete <= 0:
                hit.finish_hit()
            else:
                hit.time_to_complete = hit.time_to_complete - dt
                self.collman.add(hit)
        
        for hit_1, hit_2 in self.collman.iter_all_collisions():
            hit_1.parry(hit_2)
                
        self.collman.add(self.hero)
        map(self._actor_kick_or_add, self.actors)
        
        for obj1, obj2 in self.collman.iter_all_collisions():
            ob1_hit = isinstance(obj1, wp.Slash)
            ob2_hit = isinstance(obj2, wp.Slash)
            if ob1_hit and ob2_hit:
                pass
            elif ob1_hit and obj1.time_to_complete <= 0:
                obj2.take_hit(obj1)
            elif ob2_hit and obj2.time_to_complete <= 0:
                obj1.take_hit(obj2)
            elif not ob1_hit and not ob2_hit:
                #print obj1.fight_group, obj2.fight_group, consts['group']['hero']
                if obj1.fight_group == consts['group']['hero']:
                    obj1.stand_off(obj2)
                elif obj2.fight_group == consts['group']['hero']:
                    obj2.stand_off(obj1)
                else:
                    pass
            else:
                pass
                
            
    
    def do_hit(self, hit):

        """
        Callback from Weapon. Append Hit to Level for show.
        """

        self.add(hit, z = 2)
        
    def hit_perform(self, hit):

        """
        Callback from Weapon. Append Hit to collision manager for calculate collisions
        """

        self.hits.append(hit)
        
    def remove_hit(self, hit):

        """
        Remove overdue Hit from game.
        """

        hit.kill()
        self.hits.remove(hit)

    def on_mouse_motion(self, x, y, dx, dy):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler['d'] = (dx, dy)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler['d'] = (dx, dy)
    
    def on_mouse_press(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler[buttons] = True
    
    def on_mouse_release(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler[buttons] = False


def create_level(filename):

    """
    Create scrollable Level from tmx map
    """

    scene = cocos.scene.Scene()
    
    data = tiles.load(filename)
    back = data['Background']
    force = data['Player Level']
    scripts = data['Scripts']
    
    scroller = layer.ScrollingManager()
    player_layer = Level_Layer(scripts, force, scroller)
    
    scroller.add(back, z = -1)
    scroller.add(force, z = 0)
    scroller.add(player_layer, z = 1)

    scene.add(scroller, z = 1)
    return scene

def main():
    director.init(**consts['window'])
    lvl = create_level('map01.tmx')
    director.run(lvl)

if __name__ == "__main__":
    main()
