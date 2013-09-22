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
import hits

consts = con.consts


class Level_Collider(tiles.RectMapCollider):
    
    def collide_bottom(self, dy):
        self.wall |= con.DOWN
        self.on_ground = True
        self.vertical_speed = 0
    
    def collide_top(self, dy):
        self.wall |= con.UP
        self.vertical_speed = 0
    
    def collide_left(self, dx):
        self.wall |= con.LEFT
        #self.horizontal_speed = 0
    
    def collide_right(self, dy):
        self.wall |= con.RIGHT
        #self.horizontal_speed = 0


class Actor(cocos.sprite.Sprite, Level_Collider):
    
    is_event_handler = True
    tilemap = None
    
    def __init__(self, body):
        self.fight_group = -1
        
        self.hands = [None, None]
        
        self.body = body(self)
        super(Actor, self).__init__(self.body.img)
        
        self.cshape = cm.AARectShape(eu.Vector2(*self.position),
                                     self.body.img.width/2, self.body.img.height/2)
        
        self.on_ground = False
        self.vertical_speed = 0
        self.horizontal_speed = 0
        self.wall = con.NO_TR

        self.recovery = 0.0  # Time before moment when acton can be controlled again

        #self.schedule(self.update)
    
    actual_hit = property(lambda self: self.hands[0].actual_hit)
    height = property(lambda self: self.body.img.height)
    width = property(lambda self: self.body.img.width)
    attack_perform = property(lambda self: self.hands[0].attack_perform)
    
    def destroy(self):
        """
        Remove Actor from level
        """
        self.hands[0].dearm()
        self.fight_group = -1
        self.kill()

    def walk(self, horizontal_direction):
        """
        Move Actor in horizontal_direction with his body speed
        """
        if self.on_ground:
            d = horizontal_direction * self.body.speed
            #if abs(self.horizontal_speed + d) > self.body.speed:
            self.horizontal_speed = d

    def stay(self):
        """
        Do not move Actor
        """
        self.horizontal_speed = 0

    def attack(self, start_point, end_point):
        """
        Create Hit with Actor's Weapon. Hit start in start_point
        and end in end_point
        """
        self.start_attack(start_point)
        self.aim(end_point)
        self.perform()
        
    def _move(self, dx, dy):

        """
        Try to move Actor on dx, ndy with registrations all collisions
        with map.
        """

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
        vec = eu.Vector2(int(ndx), int(ndy))
        self.position += vec
        self.cshape.center += vec
        for hand in self.hands:
            if hand.actual_hit is not None:
                hand.actual_hit._move(vec)

    def push(self, v):
        self.horizontal_speed += v.x
        self.vertical_speed += v.y

    def update(self, dt):
        dy = self.vertical_speed * dt if self.vertical_speed != 0 else 0
        dx = self.horizontal_speed * dt if self.horizontal_speed != 0 else 0
        self._move(dx, dy)
        if not self.on_ground:
            self.vertical_speed -= consts['gravity'] * dt
        else:
            self.vertical_speed = 0
        speed = abs(self.horizontal_speed)
        d = self.horizontal_speed/speed if self.horizontal_speed != 0 else 0
        speed -= consts['rubbing'] * dt
        self.horizontal_speed = speed * d if speed >= 0 else 0

    def get_item(self, item, num=0):
        self.hands[num] = item
        item.master = self

    def jump(self):
        """
        Actor jump with his body jump speed.
        """
        self.vertical_speed = consts['params']['human']['jump_speed']
        self.on_ground = False
        
    def move_to(self, x, y):
        """
        Place Actor to x, y.
        """
        old = self.cshape.center.copy()
        vec = eu.Vector2(int(x), int(y))
        self.position = vec
        self.cshape.center = vec
        for hand in self.hands:
            if hand.actual_hit is not None:
                hand.actual_hit._move(vec - old)
    
    def stand_off(self, other):
        """
        Push aside Actor from other collidable object
        """
        s_c = self.cshape.center
        o_c = other.cshape.center
        d = o_c - s_c
        l = self.width/2 + other.width/2
        dd = l - abs(d.x)
        if d.x > 0:
            self._move(-dd, 0)
        else:
            self._move(dd, 0)

    def start_attack(self, start_point, hit_pattern=con.CHOP):
        """
        Set up start point of attack
        """
        self.hands[0].start_use(start_point, hit_pattern)
        
    def perform(self):
        """
        Send current actual_hit to Level as collidable object
        for further checking of hit or miss
        """
        self.hands[0].end_use()
    
    def aim(self, end_point):
        """
        Set up end point of attack
        """
        self.hands[0].continue_use(end_point)
        
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
                                  'd': (0, 0),
                                  mouse.LEFT: False,
                                  mouse.RIGHT: False,
                                  mouse.MIDDLE: False}
        
        self.loc_key_handler = key.KeyStateHandler()
        director.window.push_handlers(self.loc_key_handler)
        
        #Tilemaps. Setup this on Actor.
        self.scroller = scroller
        self.force_ground = force_ground
        Actor.tilemap = force_ground  # This bad

        #Setup layer for effects
        eff.Advanced_Emitter.surface = self  # This bad
        
        #Collision managers. For static global and dynamic screen objects
        self.collman = cm.CollisionManagerBruteForce()
        self.static_collman = cm.CollisionManagerBruteForce()
        
        #Lists of dynamic objs
        self.hits = []
        self.actors = []
        
        #Append ground
        #self.add(force_ground, z = 1)
        
        #Append hero
        self.hero = Actor(bd.Human)
        self.hero.get_item(wp.Standard_Weapon(self))
        self.hero.get_item(wp.Standard_Weapon(self), 1)
        #self.hero.weapon.push_handlers(self)
        #self.hero.move(200, 200)
        self.add(self.hero, z=2)
        
        #Append opponent
        self.opponent = Actor(bd.Human)
        self.opponent.get_item(wp.Standard_Weapon(self))
        self.opponent.get_item(wp.Empty_Hand(self), 1)
        #self.opponent.weapon.push_handlers(self)
        #self.opponent.move(400, 200)
        self.add(self.opponent, z=2)
        self.actors.append(self.opponent)
        
        #Move guys to location
        for sc in scripts:
            if 'player' in sc.properties:
                r = self.hero.get_rect()
                r.midbottom = sc.midbottom
                dx, dy = r.center
                self.hero.move_to(dx, dy)
            elif 'opponent' in sc.properties:
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
            if hit.time_to_complete <= 0 and not hit.completed:
                hit.finish_hit()
            elif hit.completed:
                pass
            else:
                hit.time_to_complete = hit.time_to_complete - dt
                self.collman.add(hit)
        
        for hit_1, hit_2 in self.collman.iter_all_collisions():
            hit_1.parry(hit_2)
                
        self.collman.add(self.hero)
        map(self._actor_kick_or_add, self.actors)
        
        for obj1, obj2 in self.collman.iter_all_collisions():
            ob1_hit = isinstance(obj1, hits.Slash)
            ob2_hit = isinstance(obj2, hits.Slash)
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
        self.add(hit, z=2)
        
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
    
    scroller.add(back, z=-1)
    scroller.add(force, z=0)
    scroller.add(player_layer, z=1)

    scene.add(scroller, z=1)
    return scene


def main():
    director.init(**consts['window'])
    lvl = create_level('map01.tmx')
    director.run(lvl)


if __name__ == "__main__":
    main()
