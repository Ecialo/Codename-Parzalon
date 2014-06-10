# -*- coding: utf-8 -*-
__author__ = 'ecialo'
import cocos.euclid as eu
import geometry as gm
import Box2D as b2
import effects as eff
from registry.utility import EMPTY_LIST
from registry.metric import pixels_to_tiles
from registry.metric import tiles_to_pixels
from registry.box2d import *
#import consts as con

def death(body_part):
    body_part.master.destroy()


class Body_Part(object):

    max_health = 10
    max_armor = 10

    def __init__(self, master, center, h_height, h_width,
                 stab_priority, chop_priority,
                 on_destroy_effects=EMPTY_LIST):
        self.master = master
        #print master, "BODU PART BODU"
        #print master.master, "DOBY PART Actor"

        self.health = self.max_health
        self.armor = self.max_armor

        self.on_destroy_effects = on_destroy_effects

        #box2d
        actor = master.master
        x, y = center
        box = pixels_to_tiles((h_width, h_height, (x, y), 0))
        self.b2fixture = actor.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=box),
                                                                    isSensor=True, userData=self))
        actor.b2body.fixtures[-1].filterData.categoryBits = B2BODYPART
        actor.b2body.fixtures[-1].filterData.maskBits = B2HITZONE | B2SWING

        # Center relatively body
        p = gm.Point2(center.x - h_width, center.y - h_height)
        v = eu.Vector2(h_width * 2, h_height * 2)
        self.shape = gm.Rectangle(p, v)
        self.stab_priority = stab_priority
        self.chop_priority = chop_priority

        self.attached = None

    position = property(lambda self: self.master.master.from_self_to_global(self.shape.pc))
    #horizontal_speed = property(lambda self: self.master.horizontal_speed)
    #vertical_speed = property(lambda self: self.master.vertical_speed)

    def turn(self):
        c = self.shape.pc
        self.shape.pc = (-c[0], c[1])

    def set_pos(self, pos):
        self.shape.pc = (pos[0] * self.master.master.direction, pos[1])
        if self.attached is not None:
            self.attached.shell.shape.pc = self.shape.pc
        #print 11

    def transfer(self):
        pass

    def collide(self, hit):
        """
        Body Part receive all effects from Hit
        and apply them to self
        """
        if self.master.master.fight_group != hit.base_fight_group:
            for effect in hit.effects:
                effect(self)
            if self.health <= 0:
                self.destroy()
            elif self.master.health <= 0:
                self.master.destroy()
            p = tiles_to_pixels(self.master.master.b2body.GetWorldPoint(self.b2fixture.shape.centroid))
            eff.Blood().add_to_surface(p)
            hit.complete()
        #print self.health, self.armor

    def get_on(self, item):
        if self.attached is not None:
            self.attached.drop()
        self.attached = item
        item.master = self
        item.shell.master = self.master
        self.master.body_parts.append(item.shell)

    def destroy(self):
        """
        Remove self and apply some effects
        """
        self.master.body_parts.remove(self)
        for effect in self.on_destroy_effects:
                effect(self)
