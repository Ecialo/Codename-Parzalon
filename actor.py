__author__ = 'Ecialo'

import cocos
from cocos import collision_model as cm
from cocos import tiles
from cocos import euclid as eu

import movable_object
import consts as con

consts = con.consts


class Actor(movable_object.Movable_Object):

    is_event_handler = True

    def __init__(self, body):
        self.fight_group = -1

        self.hands = []
        self.body = body(self)

        cshape = cm.AARectShape(eu.Vector2(0, 0), self.body.img.width/2, self.body.img.height/2)
        super(Actor, self).__init__(self.body.img, cshape)

        self.recovery = 0.0  # Time before moment when acton can be controlled again

        #self.schedule(self.update)

    height = property(lambda self: self.body.img.height)
    width = property(lambda self: self.body.img.width)
    #attack_perform = property(lambda self: self.hands[0].attack_perform)

    def destroy(self):
        """
        Remove Actor from level
        """
        for item in self.hands:
            item.dearm()
            item.drop()
        self.fight_group = -1
        self.kill()

    def _move(self, dx, dy):
        old = self.cshape.center.copy()
        super(Actor, self)._move(dx, dy)
        vec = self.cshape.center.copy() - old
        for hand in self.hands:
            if hand.actual_hit is not None:
                hand.actual_hit._move(vec)

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

    def push(self, v):
        self.horizontal_speed += v.x
        self.vertical_speed += v.y

    def get_item(self, item):
        self.hands.append(item)
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