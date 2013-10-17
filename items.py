__author__ = 'Ecialo'
from random import randint
from cocos import collision_model as cm
from cocos import euclid as eu
import movable_object as mova
import consts as con


def length(value):
    def add_length(master):
        master.length = value
    return add_length


def ammo(value):
    def add_ammo(master):
        master.max_ammo = value
        master.ammo = value
    return add_ammo


class Item(mova.Movable_Object):

    def __init__(self, img):
        cshape = cm.AARectShape(eu.Vector2(0, 0), img.width/2, img.height/2,)
        mova.Movable_Object.__init__(self, img, cshape)

        self.master = None

    def drop(self):
        self.position = self.master.position
        self.cshape.center = self.master.cshape.center.copy()
        self.horizontal_speed = self.master.horizontal_speed + randint(-500, 500)
        self.vertical_speed = self.master.vertical_speed + randint(-100, 100)
        self.dispatch_event('on_drop_item', self)
        self.schedule(self.update)

    def get_up(self):
        self.dispatch_event('on_get_up_item', self)

    def update(self, dt):
        mova.Movable_Object.update(self, dt)
        if self.wall & con.DOWN:
            self.dispatch_event('on_lay_item', self)
            self.unschedule(self.update)
Item.register_event_type('on_drop_item')
Item.register_event_type('on_get_up_item')
Item.register_event_type('on_lay_item')


class Usage_Item(Item):

    def __init__(self, img, first_usage, second_usage, addi_props=[]):
        Item.__init__(self, img)
        self.first_usage = first_usage(self)
        self.second_usage = second_usage(self) if second_usage is not None else self.first_usage
        self.current_usage = None

        self.on_use = False
        self.available = True

        map(lambda prop: prop(self), addi_props)

    def __call__(self, environment):
        self.push_handlers(environment)
        return self

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