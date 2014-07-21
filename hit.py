# -*- coding: utf-8 -*-
"""
1) Зоны попаданий должны создавать актёры, т.к. эти зоны не появляются из ниоткуда
2) Должно существовать минимум 2 способа срабатывания зоны: с наложением эффектов и без
3) При срабатывании с наложениями зона должна определять какую из доступных частей она задевает
"""
__author__ = 'Ecialo'


from pyglet import image

import cocos
from cocos.draw import Line
from cocos import collision_model as cm
from cocos import euclid as eu

import math
import geometry as gm
import Box2D as b2

import movable_object as mova
import collides as coll
import box
from registry.group import CHOP, STAB, SWING, MISSLE, LINE, RECTANGLE
from registry.box2d import *
from registry.metric import pixels_to_tiles
from registry.utility import EMPTY_LIST


def shape_to_cshape(shape):
    """
    Transform geometry shape to collision shape
    """
    if isinstance(shape, gm.Rectangle):
        return cm.AARectShape(shape.pc, shape.h_width, shape.h_height)
    else:
        c = shape.p + shape.v/2
        return cm.AARectShape(c, abs(shape.v.x/2), abs(shape.v.y/2))


class Swing(cocos.draw.Line):

    def __init__(self, stp, endp, master, hit_pattern=CHOP):
        self.master = master
        owner = self.master.owner
        stp = owner.from_global_to_self(stp)
        endp = owner.from_global_to_self(endp)
        self.fight_group = master.owner.fight_group | SWING
        self.base_fight_group = master.owner.fight_group
        super(Swing, self).__init__(stp, endp, (0, 255, 0, 255))

        self.completed = False
        self._time_to_complete = 0.0
        self._color_c = 0.0

        self.b2fixture = None
        self.cshape = None
        self.trace = None
        self.contacts = []

        self.hit_pattern = hit_pattern
        self.features = set()

    effects = property(lambda self: filter(None, map(lambda eff: eff(self), self.master.effects)))

    def update(self, dt):
        if self.time_to_complete <= 0.0:
            self.complete()
        else:
            self.time_to_complete -= dt

    def uncompleteness(self):
        return self.time_to_complete/self.master.swing_time

    def _change_time_to_complete(self, time):
        """
        Update time to complete with representable color
        """
        self._time_to_complete = time
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

    def on_begin_contact(self, fixture):
        fixcat = fixture.filterData.categoryBits
        if fixcat & B2BODYPART:
            self.contacts.append(fixture.userData)
        elif fixcat & B2SWING:
            fixture.userData.collide(self)

    def on_end_contact(self, fixture):
        if fixture.filterData.categoryBits & B2ACTOR:
            self.contacts.remove(fixture.body.userData)

    def collide(self, other):
        other._collide_slash(self)

    def _collide_slash(self, other):
        coll.collide_slash_slash(self, other)

    def _collide_actor(self, other):
        coll.collide_actor_slash(other, self)

    def _collide_hit_zone(self, other):
        coll.collide_slash_hit_zone(self, other)

    def aim(self, vec):
        end = self.start + vec.normalize()*self.master.length
        self.end = end

    def perform(self, time):
        """
        Morph line into real collideable figure.
        """
        #Define geometry and time data
        actor = self.master.owner
        v1 = actor.b2body.GetLocalPoint(pixels_to_tiles((self.start.x, self.start.y)))
        v2 = actor.b2body.GetLocalPoint(pixels_to_tiles((self.end.x, self.end.y)))
        if v2.x <= v1.x:
            v1, v2 = v2, v1
        vlen = math.sqrt((v2.x-v1.x)*(v2.x-v1.x)+(v2.y-v1.y)*(v2.y-v1.y))
        vcent = ((v1.x+v2.x)/2.0, (v1.y+v2.y)/2.0)
        vangle = math.asin((v2.y-v1.y)/vlen)
        v = self.end - self.start
        start = gm.Point2(self.start.x, self.start.y)
        self.trace = gm.LineSegment2(start, v)
        self.cshape = shape_to_cshape(self.trace)
        self.set_time_to_complete(time)
        self.b2fixture = actor.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=(vlen, 0,
                                                                                                 vcent, vangle)),
                                                                    isSensor=True, userData=self))
        self.b2fixture.filterData.categoryBits = B2SWING
        self.b2fixture.filterData.maskBits = B2HITZONE | B2SWING | B2BODYPART
        actor.world.addEventHandler(self.b2fixture, self.on_begin_contact, self.on_end_contact)
        self.schedule(self.update)

    def set_batch(self, _):
        pass

    def complete(self, parried=False):
        """
        End life of this line
        """
        if self.completed:
            return
        self.completed = True
        self.unschedule(self.update)
        if not parried:
            for bodypart in self.contacts:
                bodypart.collide(self)
        self.fight_group = -1
        self.base_fight_group = -1
        self.master.owner.world.destroy_fixture(self.b2fixture)
        self.master.complete()
        self.kill()

    def _move(self, vec):
        """
        Move end and start points of line
        """
        self.position += vec
        if self.trace is not None:
            self.trace.p += vec
            self.cshape.center += vec


def non_gravity_update(self, dt):
    start_point = self.cshape.center.copy()
    super(Hit_Zone, self).update(dt)
    v = self.cshape.center - start_point
    self.trace.p += v


class Hit_Zone(mova.Movable_Object):

    def __init__(self, master, img, vector, speed, position, hit_shape,
                 effects=EMPTY_LIST):
        if hit_shape is RECTANGLE:
            trace = gm.Rectangle(gm.Point2(0, 0), eu.Vector2(img.width, img.height))
            trace.pc = position
        elif hit_shape is LINE:
            start_point = gm.Point2(position[0] - img.width/2, position[1] - img.height/2)
            v = vector/abs(vector)*img.width
            trace = gm.LineSegment2(start_point, v)
            #TODO add rotation
        self.hit_shape = hit_shape
        self.trace = trace
        cshape = shape_to_cshape(self.trace)
        v = vector/abs(vector) if abs(vector) != 0 else eu.Vector2(0,0)
        v *= speed
        mova.Movable_Object.__init__(self, img, cshape, position, v.y, v.x)

        self.master = master
        self.fight_group = master.owner.fight_group | MISSLE
        self.base_fight_group = master.owner.fight_group

        self.features = set()
        self.hit_pattern = STAB

        self.completed = False

        self.time_to_complete = 0.1
        self.time = 0.1

        if effects is not EMPTY_LIST:
            self.effects = filter(None, map(lambda eff: eff(self), effects))
        else:
            self.effects = filter(None, map(lambda eff: eff(self), self.master.effects))

        self.schedule(self.update)

    def setup_b2body(self):
        super(Hit_Zone, self).setup_b2body()
        cshape = self.cshape
        hit_shape = self.hit_shape
        img = self.image
        if hit_shape is RECTANGLE:
            rx, ry = pixels_to_tiles((cshape.rx, cshape.ry))
            self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=(rx, ry)), isSensor=True,
                                                      userData=self))
        elif hit_shape is LINE:
            r = pixels_to_tiles(img.width/2.0)
            self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=(r, 0)),
                                                      isSensor=True, userData=self))
        self.b2body.gravityScale = 0
        self.b2body.fixtures[-1].filterData.categoryBits = B2HITZONE
        self.b2body.fixtures[-1].filterData.maskBits = B2HITZONE | \
                                                       B2SWING | B2LEVEL | B2BODYPART
        self.world.addEventHandler(self.b2body.fixtures[-1], self.on_begin_contact, self.on_end_contact)

    def update(self, dt):
        self.time -= dt

    def uncompleteness(self):
        return max(0.0, self.time)/self.time_to_complete

    def complete(self, parried=False):
        if self.completed:
            return
        self.completed = True
        self.world.destroy_body(self.b2body)
        self.master.destroy_missile(self)

    def on_begin_contact(self, fixture):
        fixcat = fixture.filterData.categoryBits
        if fixcat & B2LEVEL:
            self.complete()
        else:
            fixture.userData.collide(self)

    def on_end_contact(self, fixture):
        pass

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


class Invisible_Hit_Zone(Hit_Zone):

    def __init__(self, master, width, height, v, speed, position, effects=EMPTY_LIST):
        img = image.SolidColorImagePattern((0, 0, 0, 0)).create_image(width, height)
        Hit_Zone.__init__(self, master, img, v, speed, position, RECTANGLE, effects)


#TODO: move to box2d
class Missile(Hit_Zone):

    update = non_gravity_update

    def uncompleteness(self):
        return 0.5


class Cool_Swing(Line):

    """
    Работает в 3 этапа
    1) Прицеливание. На этом этапе взмах можно двигать и вращать, он виден, но эффекта не оказывает
    2) Исполнение. На этом этапе взмах можно паррировать и он может паррировать.
    3) Выполнение. Срабатывают эффекты и всё завершается.
    """

    def __init__(self, actor, sp, ep):
        super(Cool_Swing, self).__init__((0, 0), (0, 0), (255, 0, 0, 255))
        self.actor = actor
        self.to_hit = set()

    def setup_b2body(self):
        pass

    def perform(self):
        pass

    def negate(self):
        pass