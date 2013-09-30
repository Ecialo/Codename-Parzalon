# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"
__date__ = "$24.08.2013 12:52:47$"

import pyglet

from cocos import collision_model as cm
from cocos import euclid as eu

#import geometry as gm
import consts as con
import on_hit_effects as on_h
import hits as hit
import movable_object as mova

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


class Item(mova.Movable_Object):

    def __init__(self, img):
        cshape = cm.AARectShape(eu.Vector2(0, 0), img.width/2, img.height/2,)
        mova.Movable_Object.__init__(self, img, cshape)
        pyglet.event.EventDispatcher.__init__(self)

        self.master = None
        self.on_use = False

    def start_use(self, *args):
        self.on_use = True

    def continue_use(self, *args):
        pass

    def end_use(self, *args):
        self.on_use = False

    def drop(self):
        self.position = self.master.position
        self.cshape.center = self.master.cshape.center.copy()
        self.horizontal_speed = self.master.horizontal_speed
        self.vertical_speed = self.master.vertical_speed
        self.dispatch_event('on_drop_item', self)
        self.schedule(self.update)

    def get_up(self):
        self.dispatch_event('on_get_up_item', self)

    def update(self, dt):
        mova.Movable_Object.update(self, dt)
        if self.wall & con.DOWN:
            self.dispatch_event('on_lay_item', self)
            self.unschedule(self.update)
Item.register_event_type('on_drop_item')
Item.register_event_type('on_get_up_item')
Item.register_event_type('on_lay_item')


class Weapon(Item):
    
    def __init__(self, name, img, length, weight, effects, environment):
        super(Weapon, self).__init__(img)
        self.name = name
        self.hit_type = hit.Slash
        self.length = length
        self.weight = weight

        self.chop_time = consts['test_slash_time']
        self.stab_time = consts['test_slash_time']
        
        self.effects = effects
        
        self.actual_hit = None
        self.attack_perform = False

        self.push_handlers(environment)
    
    def start_use(self, *args):
        """
        Create line what start from closest to start point possible place near Actor.
        """
        super(Weapon, self).start_use()
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
        self.dispatch_event('on_do_hit', self.actual_hit)
        
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
        self.dispatch_event('on_perform_hit', self.actual_hit)
        
    def destroy(self):
        """
        Remove current Hit and complete attack
        """
        self.dispatch_event('on_remove_hit', self.actual_hit)
        self.attack_perform = False
        self.actual_hit = None
        self.on_use = False
        #print "ololo"
        
    def dearm(self):
        """
        Weapon now can't do anything
        """
        if self.attack_perform and self.actual_hit is not None:
            self.destroy()
        elif self.actual_hit is not None:
            self.actual_hit.kill()
        #self.pop_handlers()
        
Weapon.register_event_type('on_do_hit')
Weapon.register_event_type('on_perform_hit')
Weapon.register_event_type('on_remove_hit')


class Throwable_Weapon(Weapon):

    def __init__(self, name, img, length, weight, effects, throw_speed, environment):
        Weapon.__init__(self, name, img, length, weight, effects, environment)
        self.throw_speed = throw_speed
        self.alt = 0

    def start_use(self, *args):
        if args[-1] == 0:
            Weapon.start_use(self, *args)
            self.alt = 0
        else:
            self.on_use = True
            self.alt = 1

    def continue_use(self, *args):
        if self.alt == 0:
            Weapon.continue_use(self, *args)
        else:
            pass

    def end_use(self, *args):
        if self.alt == 0:
            Weapon.end_use(self, *args)
        else:
            end_point = eu.Vector2(*args[0])
            v = end_point - self.master.cshape.center
            hit_zone = hit.Hit_Zone(self, self.image, v, 300, self.master.position)
            self.actual_hit = hit_zone
            self.dispatch_event('on_launch_missile', hit_zone)
            self.on_use = False
            hit_zone.show_hitboxes()
            self.master.hands.remove(self)

    def destroy_missile(self):
        self.dispatch_event('on_remove_missile', self.actual_hit)
        self.actual_hit = None
Throwable_Weapon.register_event_type('on_launch_missile')
Throwable_Weapon.register_event_type('on_remove_missile')


class Knife(Throwable_Weapon):
    def __init__(self, environment):
        super(Throwable_Weapon, self).__init__("kn",
                                               consts['img']['knife'],
                                               50,
                                               20,
                                               [on_h.damage(1), on_h.cleave],
                                               environment)


class Standard_Weapon(Weapon):

    def __init__(self, environment):
        super(Standard_Weapon, self).__init__("wp",
                                              consts['img']['weapon'],
                                              100,
                                              20,
                                              [on_h.damage(5), on_h.knock_back(100)],
                                              environment)
