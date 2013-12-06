__author__ = 'Ecialo'

import cocos
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


class Movable_Object(cocos.sprite.Sprite, Level_Collider):

    tilemap = None

    def __init__(self, img, cshape=None, position=(0, 0), vertical_speed=0, horizontal_speed=0):
        cocos.sprite.Sprite.__init__(self, img, position)
        self.image = img
        self.vertical_speed = vertical_speed
        self.horizontal_speed = horizontal_speed
        if cshape is not None:
            self.cshape = cshape
            self.cshape.center = eu.Vector2(*position)
        self.wall = con.NO_TR
        self.on_ground = False

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
        if self.on_ground:
            speed -= consts['rubbing'] * dt
        self.horizontal_speed = speed * d if speed >= 0 else 0