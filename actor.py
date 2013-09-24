__author__ = 'Ecialo'

import cocos
from cocos import collision_model as cm
from cocos import tiles
from cocos import euclid as eu

import consts as con

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

        self.hands = []

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

    height = property(lambda self: self.body.img.height)
    width = property(lambda self: self.body.img.width)
    #attack_perform = property(lambda self: self.hands[0].attack_perform)

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