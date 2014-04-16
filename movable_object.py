__author__ = 'Ecialo'

import cocos
from cocos import tiles
from cocos import euclid as eu

import Box2D as b2

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
    world = None

    def __init__(self, img, cshape=None, position=(0, 0), vertical_speed=0, horizontal_speed=0):
        cocos.sprite.Sprite.__init__(self, img, position)
        #print self.world is None
        self.image = img
        self.vertical_speed = vertical_speed
        self.horizontal_speed = horizontal_speed
        pix_to_tile = con.pixel_value_to_tiles_value
        self.b2body = self.world.CreateDynamicBody(position=pix_to_tile(position), fixedRotation=True, userData=self)
        if cshape:
            #self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=pix_to_tile((cshape.rx, cshape.ry)))))
            self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(
                vertices=pix_to_tile([(-cshape.rx, cshape.ry), (-cshape.rx, -cshape.ry+1), (-cshape.rx+1, -cshape.ry),
                                      (cshape.rx-1, -cshape.ry), (cshape.rx, -cshape.ry+1), (cshape.rx, cshape.ry)]),
                friction=0)))
            self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2EdgeShape(vertex1=pix_to_tile((-cshape.rx, -cshape.ry)),
                                                                           vertex2=pix_to_tile((cshape.rx, -cshape.ry))),
                                                      isSensor=True))
            self.world.contactListener.addEventHandler(self.b2body.fixtures[-1], self.onGroundBegin, self.onGroundEnd)
        self.cshape = cshape
        if cshape:
            self.cshape.center = eu.Vector2(*position)
        self.wall = con.NO_TR
        self.ground_count = 0
        self.on_ground = False

    # def move_to(self, x, y):
    #     old = self.cshape.center.copy()
    #     vec = eu.Vector2(int(x), int(y))
    #     self._move(*(vec-old))

    def set_position(self, x):
        val = con.tiles_value_to_pixel_value(x)
        self.position = val
        self.cshape.center = val

    def _move(self, dx, dy):
        """
        Try to move Actor on dx, ndy with registrations all collisions
        with map.
        """
        self.b2move(dx, dy)
        return
        # self.on_ground = False
        # self.wall = con.NO_TR
        # #if self.cshape:
        # #    x, y = self.cshape.center
        # #    width, height = self.cshape.rx*2, self.cshape.ry*2
        # #    rect = Rect(x, y, width, height)
        # #else:
        # rect = self.get_rect()
        # orig = rect.copy()
        # last = rect.copy()
        # new = last.copy()
        # new.x += dx
        # self.collide_map(self.tilemap, last, new, dx, 0.0)
        # last = new.copy()
        # new.y += dy
        # self.collide_map(self.tilemap, last, new, 0.0, dy)
        # ndx, ndy = new.x - orig.x, new.y - orig.y
        # vec = eu.Vector2(int(ndx), int(ndy))
        # self.position += vec
        # self.cshape.center += vec

    def onGroundBegin(self, fixture):
        self.ground_count += 1
        self.on_ground = True

    def onGroundEnd(self, fixture):
        self.ground_count -= 1
        if self.ground_count == 0:
            self.on_ground = False

    def update(self, dt):
        self.b2update()
        return
        # dy = self.vertical_speed * dt if self.vertical_speed != 0 else 0
        # dx = self.horizontal_speed * dt if self.horizontal_speed != 0 else 0
        # self._move(dx, dy)
        # if not self.on_ground:
        #     self.vertical_speed -= consts['gravity'] * dt
        # else:
        #     self.vertical_speed = 0
        # speed = abs(self.horizontal_speed)
        # d = self.horizontal_speed/speed if self.horizontal_speed != 0 else 0
        # if self.on_ground:
        #     speed -= consts['rubbing'] * dt
        # self.horizontal_speed = speed * d if speed >= 0 else 0

    def b2move(self, dx, dy):
        # print (dx,dy)
        # print con.pixel_value_to_tiles_value((dx,dy))
        self.b2body.position += (dx, dy)
        #self.position = (self.position[0]+dx, self.position[1]+dy)

    def b2update(self):
        if self.on_ground:
            self.b2body.linearVelocity = (self.horizontal_speed, self.vertical_speed)
        else:
            #(self.horizontal_speed, self.vertical_speed) = con.tiles_value_to_pixel_value(self.b2body.linearVelocity)
            (self.horizontal_speed, self.vertical_speed) = (0, 0)
        #print (self.b2body.linearVelocity)
        self.set_position(self.b2body.position)
        #self.cshape.center = con.tiles_value_to_pixel_value(self.b2body.position)
        # for contact_edge in self.b2body.contacts:
        #     contact = contact_edge.contact
        #     #print "AABB"
        #     if contact.touching:
        #         if contact.fixtureB.body.userData.actions[0].fight_group == 1:
        #             print "LOL"