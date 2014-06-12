__author__ = 'Ecialo'
from random import randint
from cocos import collision_model as cm
from cocos import euclid as eu
from cocos.tiles import Tile
import Box2D as b2
import movable_object as mova

from registry.inventory import HAND
from registry.utility import EMPTY_LIST
from registry.item import SMALL, LARGE
from registry.metric import pixels_to_tiles
from registry.box2d import *


class Item(mova.Movable_Object):

    slot = None
    size = SMALL

    def __init__(self, img):
        cshape = cm.AARectShape(eu.Vector2(0, 0), img.width/2, img.height/2,)
        mova.Movable_Object.__init__(self, img, cshape)

        self.master = None

        self.inventory_representation = Tile(1, {'item': self}, img)
        self.item_update = None

    def __call__(self, environment):
        try:
            self.pop_handlers()
        except AssertionError:
            pass
        self.push_handlers(environment)
        return self

    def destroy(self):
        pass

    def drop(self):
        self.position = self.master.position
        if self.item_update:
            self.master.stop_interact_with_item(self)
        self.cshape.center = eu.Vector2(self.position[0], self.position[1])
        rx, ry = pixels_to_tiles((self.cshape.rx, self.cshape.ry))
        self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=(rx, ry)), userData=self))
        self.b2body.fixtures[-1].filterData.categoryBits = B2ITEM
        self.b2body.fixtures[-1].filterData.maskBits = B2LEVEL
        self.b2body.fixtures[-1].friction = 10
        x, y = pixels_to_tiles((self.cshape.center.x, self.cshape.center.y))
        self.b2body.position = (x, y)
        self.b2body.linearVelocity.x = self.master.b2body.linearVelocity.x + pixels_to_tiles(randint(-500, 500))
        self.b2body.linearVelocity.y = self.master.b2body.linearVelocity.y + pixels_to_tiles(randint(-100, 100))
        self.dispatch_event('on_drop_item', self)
        self.master = None
        self.schedule(self.update)

    def get_up(self):
        self.dispatch_event('on_get_up_item', self)

    def set_master(self, master):
        self.master = master
Item.register_event_type('on_drop_item')
Item.register_event_type('on_get_up_item')
Item.register_event_type('on_lay_item')


class Usage_Item(Item):

    slot = HAND
    size = LARGE

    def __init__(self, img, first_usage, second_usage,
                 attributes=EMPTY_LIST):
        Item.__init__(self, img)
        self.first_usage = first_usage(self)
        self.second_usage = second_usage(self) if second_usage is not None else self.first_usage
        self.current_usage = None

        self.on_use = False
        self.available = True

        map(lambda prop: prop(self), attributes)

    def start_use(self, *args):
        alt = args[-1]
        if alt:
            self.current_usage = self.second_usage
        else:
            self.current_usage = self.first_usage
        self.on_use = True
        self.current_usage.start_use(*args)

    def continue_use(self, *args):
        self.current_usage.continue_use(*args)

    def end_use(self, *args):
        self.current_usage.end_use(*args)

    def attached_move(self, v):
        if self.current_usage is not None:
            self.current_usage.move(v)

    def from_global_to_self(self, *args):
        return self.master.from_global_to_self(*args)

    def from_self_to_global(self, *args):
        return self.master.from_self_to_global(*args)

    def drop(self):
        if self.on_use:
            self.current_usage.complete()
        Item.drop(self)
Usage_Item.register_event_type('on_launch_missile')
Usage_Item.register_event_type('on_remove_missile')
Usage_Item.register_event_type('on_do_hit')
Usage_Item.register_event_type('on_perform_hit')
Usage_Item.register_event_type('on_remove_hit')
