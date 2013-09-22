__author__ = 'Ecialo'
#import pyglet

import cocos
from cocos import collision_model as cm
#from cocos import euclid as eu

import geometry as gm
import consts as con
import effects as eff
#import on_hit_effects as on_h

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
        self.fight_group = master.master.fight_group + consts['slash_fight_group']
        self.base_fight_group = master.master.fight_group
        super(Slash, self).__init__(stp, endp, (0, 255, 0, 255))

        self._time_to_complete = 0.0
        self._color_c = 0.0

        self.cshape = None
        self.trace = None

        self.hit_pattern = hit_pattern

    effects = property(lambda self: self.master.effects)

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

    def finish_hit(self):
        """
        End life of this line
        """
        self.master.finish_hit()

    def _move(self, vec):
        """
        Move end and start points of line
        """
        self.start += vec
        self.end += vec
        if self.master.attack_perform:
            self.trace.p += vec
            self.cshape.center += vec

    def parry(self, other):
        """
        Parry consider successful then two lines create defined angle
        """
        self_uncompleteness = self.time_to_complete/self.master.stab_time if self.hit_pattern == con.STAB \
            else self.time_to_complete/self.master.chop_time
        other_uncompleteness = other.time_to_complete/other.master.stab_time if other.hit_pattern == con.STAB \
            else other.time_to_complete/other.master.chop_time
        first = self if self_uncompleteness < other_uncompleteness else other
        #second = self if first is other else other
        if first.hit_pattern is con.STAB:
            return
        p = self.trace.intersect(other.trace)
        if p is not None and self._cross_angle(other) <= consts['parry_cos_disp']:
            #print eff.Sparkles.add_to_surface
            #print p
            eff.Sparkles().add_to_surface(p)
            other.finish_hit()
            self.finish_hit()

    def _cross_angle(self, other):
        """
        Calculate cos between two lines
        """
        #Cos of angle between two hit lines
        v1 = self.trace.v
        v2 = other.trace.v
        angle = abs((v1.x * v2.x + v1.y * v2.y)/(abs(v1)*abs(v2)))
        #print angle
        return angle