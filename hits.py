__author__ = 'Ecialo'
#import pyglet

import cocos
from cocos import collision_model as cm
from cocos import euclid as eu
#from cocos import layer

import geometry as gm
import consts as con
#import effects as eff
import movable_object as mova
import collides as coll
import box
from collides import cross_angle

consts = con.consts


def shape_to_cshape(shape):
    """
    Transform geometry shape to collision shape
    """
    if isinstance(shape, gm.Rectangle):
        return cm.AARectShape(shape.pc, shape.h_width, shape.h_height)
    else:
        c = shape.p + shape.v/2
        return cm.AARectShape(c, abs(shape.v.x/2), abs(shape.v.y/2))


class Slash(cocos.draw.Line):

    def __init__(self, stp, endp, master, hit_pattern=con.CHOP):
        self.master = master
        self.fight_group = master.owner.fight_group + consts['slash_fight_group']
        self.base_fight_group = master.owner.fight_group
        super(Slash, self).__init__(stp, endp, (0, 255, 0, 255))

        self.completed = False
        self._time_to_complete = 0.0
        self._color_c = 0.0

        self.cshape = None
        self.trace = None

        self.hit_pattern = hit_pattern
        self.features = set()

    effects = property(lambda self: filter(None, map(lambda eff: eff(self), self.master.effects)))

    def uncompleteness(self):
        return self.time_to_complete/self.master.swing_time

    def _change_time_to_complete(self, time):
        """
        Update time to complete with representable color
        """
        self._time_to_complete = time
        #print 111
        val = int(time * self._color_c)
        self.color = (255 - val, val, 0, 255)

    time_to_complete = property(lambda self: self._time_to_complete,
                                _change_time_to_complete)

    def set_time_to_complete(self, time):
        """
        Init time and set color of line to dangerous red
        """
        self._time_to_complete = time
        self._color_c = 255.0 / time

    def collide(self, other):
        other._collide_slash(self)

    def _collide_slash(self, other):
        coll.collide_slash_slash(self, other)

    def _collide_actor(self, other):
        coll.collide_actor_slash(other, self)

    def _collide_hit_zone(self, other):
        coll.collide_slash_hit_zone(self, other)

    def perform(self, time):
        """
        Morph line into real collideable figure.
        """
        #Define geometry and time data
        v = self.end - self.start
        start = gm.Point2(self.start.x, self.start.y)
        self.trace = gm.LineSegment2(start, v)
        self.cshape = shape_to_cshape(self.trace)
        self.set_time_to_complete(time)

    def complete(self):
        """
        End life of this line
        """
        if self.completed:
            return
        self.completed = True
        self.master.complete()

    def _move(self, vec):
        """
        Move end and start points of line
        """
        self.start += vec
        self.end += vec
        if self.trace is not None:
            self.trace.p += vec
            self.cshape.center += vec


def on_level_collide_destroy(update_fun):

    def dec_update(self, dt):
        #print self.wall
        update_fun(self, dt)
        if self.wall is not con.NO_TR:
            print self.wall
            self.complete()
    return dec_update


def non_gravity_update(self, dt):
    #print self.position, self.cshape.center,
    start_point = self.cshape.center.copy()
    dy = self.vertical_speed * dt if self.vertical_speed != 0 else 0
    dx = self.horizontal_speed * dt if self.horizontal_speed != 0 else 0
    self._move(dx, dy)
    #print start_point, self.cshape.center
    v = self.cshape.center - start_point
    #print v
    self.trace.p += v
    #print self.trace.p
    #print self.wall


class _Hit_Zone(mova.Movable_Object):

    def __init__(self, master, img, vector, speed, position, hit_shape):
        #cshape = cm.AARectShape(eu.Vector2(*position), img.width/2, img.height/2)
        if hit_shape is con.RECTANGLE:
            trace = gm.Rectangle(gm.Point2(0, 0), eu.Vector2(img.width, img.height))
            trace.pc = position
        elif hit_shape is con.LINE:
            start_point = gm.Point2(position[0] - img.width/2, position[1] - img.height/2)
            v = vector/abs(vector)*img.width
            trace = gm.LineSegment2(start_point, v)
            #TODO add rotation
        self.hit_shape = hit_shape
        self.trace = trace
        cshape = shape_to_cshape(self.trace)
        v = vector/abs(vector) * speed
        mova.Movable_Object.__init__(self, img, cshape, position, v.y, v.x)
        self.master = master
        self.fight_group = master.owner.fight_group + consts['missile_fight_group']
        self.base_fight_group = master.owner.fight_group
        self.features = set()
        self.hit_pattern = con.STAB

        self.completed = False

        self.schedule(self.update)
        #print self.update

    update = on_level_collide_destroy(non_gravity_update)
    effects = property(lambda self: filter(None, map(lambda eff: eff(self), self.master.effects)))

    def uncompleteness(self):
        return 0.0

    def complete(self):
        if self.completed:
            return
        self.completed = True
        self.master.destroy_missile(self)

    def collide(self, other):
        other._collide_hit_zone(self)

    def _collide_hit_zone(self, other):
        coll.collide_hit_zone_hit_zone(self, other)

    def _collide_actor(self, other):
        coll.collide_actor_hit_zone(other, self)

    def _collide_slash(self, other):
        coll.collide_slash_hit_zone(other, self)

    def show_hitboxes(self):
        shape = self.trace.copy()
        shape.pc = (0, 0)
        self.add(box.Box(shape, (255, 0, 0, 255)), z=5)


class _Visible_Hit_Zone(_Hit_Zone):
    pass


class _Invisible_Hit_Zone(_Hit_Zone):
    pass


def Hit_Zone(master, img, v, speed, position=(0, 0), hit_shape = con.RECTANGLE):
        if img is None:
            return _Invisible_Hit_Zone()
        else:
            return _Visible_Hit_Zone(master, img, v, speed, position, hit_shape)