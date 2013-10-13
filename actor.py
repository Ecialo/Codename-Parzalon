__author__ = 'Ecialo'

#import cocos
from cocos import collision_model as cm
from cocos import euclid as eu

import movable_object
import consts as con
import collides as coll

consts = con.consts


def animate(func):
    def decorate(*args, **kwargs):
        if args[0].state != func.__name__:
            args[0].state = func.__name__
            args[0].image = args[0].body.anim[func.__name__]
        func(*args, **kwargs)
    return decorate


class Actor(movable_object.Movable_Object):

    is_event_handler = True

    def __init__(self, body):
        self.fight_group = -1

        self.direction = 1

        self.hands = []
        self.body = body(self)
        self.state = 'stay'

        cshape = cm.AARectShape(eu.Vector2(0, 0), self.body.img.width/2, self.body.img.height/2)
        super(Actor, self).__init__(self.body.img, cshape)

        self.recovery = 0.0  # Time before moment when acton can be controlled again

        #self.schedule(self.update)

    height = property(lambda self: self.body.img.height)
    width = property(lambda self: self.body.img.width)
    #attack_perform = property(lambda self: self.hands[0].attack_perform)

    def collide(self, other):
        other._collide_actor(self)

    def _collide_actor(self, other):
        coll.collide_actor_actor(self, other)

    def _collide_hit_zone(self, other):
        coll.collide_actor_hit_zone(self, other)

    def _collide_slash(self, other):
        coll.collide_actor_slash(self, other)

    def destroy(self):
        """
        Remove Actor from level
        """
        for item in self.hands:
            item.drop()
        for armor in filter(lambda x: (x.slot - con.ARMOR > 0), self.body.body_parts):
            armor.drop()
        self.fight_group = -1
        self.kill()

    def _move(self, dx, dy):
        old = self.cshape.center.copy()
        super(Actor, self)._move(dx, dy)
        vec = self.cshape.center.copy() - old
        map(lambda hand: hand.attached_move(vec), self.hands)

    @animate
    def walk(self, horizontal_direction):
        """
        Move Actor in horizontal_direction with his body speed
        """
        if self.on_ground:
            d = horizontal_direction * self.body.speed
            #if abs(self.horizontal_speed + d) > self.body.speed:
            self.horizontal_speed = d
            if self.direction != horizontal_direction:
                self.turn()

    @animate
    def stay(self):
        """
        Do not move Actor
        """
        self.horizontal_speed = 0

    def turn(self):
        self.direction = -self.direction
        self.body.turn()

    def push(self, v):
        self.horizontal_speed += v.x
        self.vertical_speed += v.y

    def get_item(self, item):
        if item.slot == con.HAND:
            self.hands.append(item)
            item.master = self
        else:
            for body_part in self.body.body_parts:
                if body_part.slot is item.slot:
                    body_part.get_on(item)
                    break

    @animate
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
        map(lambda hand: hand.attached_move(vec - old), self.hands)

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