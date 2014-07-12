# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from pyglet.event import EventDispatcher
from cocos import collision_model as cm
from cocos import euclid as eu
from cocos.batch import BatchableNode
import Box2D as b2
import movable_object
from registry.metric import TILE_SIZE_IN_PIXELS
from registry.item import MAIN
from registry.box2d import *
from registry.metric import pixels_to_tiles, tiles_to_pixels
from registry.utility import EMPTY_LIST
from pyglet import image
import collides as coll
from state_machine import State_Machine
from inventory import Inventory


def animate(func):
    def decorate(*args, **kwargs):
        if args[0].state != func.__name__:
            args[0].state = func.__name__
            args[0].image = args[0].body.anim[func.__name__]
        func(*args, **kwargs)
    decorate.__name__ = func.__name__
    return decorate


def activity(func):
    def decorate(*args, **kwargs):
            if args[0].state != func.__name__:
                map(args[0].body.recalculate_body_part_position, args[0].body.parts_pos[func.__name__])
            func(*args, **kwargs)
    decorate.__name__ = func.__name__
    return decorate


class Launcher(EventDispatcher):

    def __init__(self, master):
        EventDispatcher.__init__(self)
        self.master = master
        self.owner = master

    def launch(self, missile):
        self.dispatch_event('on_launch_missile', missile)

    def destroy_missile(self, missile):
        self.dispatch_event('on_remove_missile', missile)
Launcher.register_event_type('on_launch_missile')
Launcher.register_event_type('on_remove_missile')


class Actor(movable_object.Movable_Object):

    is_event_handler = True

    def __init__(self, body):
        cshape = cm.AARectShape(eu.Vector2(0, 0), TILE_SIZE_IN_PIXELS/2, body.img.height/2)
        super(Actor, self).__init__(body.img, cshape=cshape)

        self.fight_group = -1

        self.direction = 1

        self.owner = self
        self.body = body(self)
        self.launcher = Launcher(self)
        self.state = 'stand'
        self.inventory = Inventory(self)

        self.ground_count = 0
        self.on_ground = False

        self.recovery = 0.0  # Time before moment when acton can be controlled again

    height = property(lambda self: self.body.img.height)
    width = property(lambda self: self.body.img.width)

    def setup_b2body(self):
        super(Actor, self).setup_b2body()
        pix_to_tile = pixels_to_tiles
        rx, ry = pix_to_tile((self.cshape.rx, self.cshape.ry))
        self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(vertices=[(-rx, ry), (-rx, -ry+0.1),
                                                                                    (-rx+0.1, -ry), (rx-0.1, -ry),
                                                                                    (rx, -ry+0.1), (rx, ry)])))
        self.b2body.fixtures[-1].filterData.categoryBits = B2SMTH | B2ACTOR
        self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2EdgeShape(vertex1=(-rx, -ry), vertex2=(rx, -ry)),
                                                  isSensor=True))
        self.b2body.fixtures[-1].filterData.categoryBits = B2GNDSENS
        self.b2body.fixtures[-1].filterData.maskBits = B2LEVEL | B2ACTOR
        self.world.addEventHandler(self.b2body.fixtures[-1], self.on_ground_begin, self.on_ground_end)

    def use_item(self, item_type, trigger, args):       # MAIN or SECONDARY
        if item_type is MAIN:
            item = self.inventory.main_item
        else:
            item = self.inventory.secondary_item

        if not item:
            return
        if trigger and not item.on_use and item.available:
            item.start_use(*args)
        elif trigger and item.on_use and item.available:
            item.continue_use(*args)
        elif not trigger and item.on_use and item.available:
            item.end_use(*args)

    def start_interact_with_item(self, item):
        if item and item.item_update:
            self.schedule(item.item_update)

    def stop_interact_with_item(self, item):
        if item and item.item_update:
            self.unschedule(item.item_update)

    def collide(self, other):
        other._collide_actor(self)

    def _collide_actor(self, other):
        coll.collide_actor_actor(self, other)

    def _collide_hit_zone(self, other):
        coll.collide_actor_hit_zone(self, other)

    def _collide_slash(self, other):
        coll.collide_actor_slash(self, other)

    def activate_trigger(self, trigger):
        self.dispatch_event('on_activate_trigger', trigger, self)

    def put_item(self, item):
        self.inventory.put_item(item)

    def open(self):
        self.inventory.open()

    def close(self):
        self.inventory.close()

    def destroy(self):
        """
        Remove Actor from level
        """
        if self.fight_group > 0:
            for armor in filter(lambda x: (x.attached is not None), self.body.body_parts):
                armor.attached.drop()
            self.fight_group = -1
            self.remove_action(self.actions[0])
            self.kill()
            self.dispatch_event('on_death', self)

    def transfer(self):
        self.inventory.transfer()
        super(Actor, self).transfer()
        self.ground_count = 0
        self.on_ground = True

    #@activity
    def move(self, horizontal_direction):
        """
        Move Actor in horizontal_direction with his body speed
        """
        if self.on_ground:
            d = horizontal_direction * self.body.speed
            self.b2body.linearVelocity.x = d
            if self.direction != horizontal_direction:
                self.turn()

    @activity
    def stand(self):
        """
        Do not move Actor
        """
        self.b2body.linearVelocity.x = 0

    @activity
    def sit(self):
        self.b2body.linearVelocity.x = 0

    def turn(self):
        self.direction = -self.direction
        self.body.turn()

    def push(self, v):
        self.b2body.linearVelocity += v

    @activity
    def jump(self):
        """
        Actor jump with his body jump speed.
        """
        if self.on_ground:
            self.b2body.linearVelocity.y = 11   # TODO сделать по людски

    def move_to(self, x, y):
        """
        Place Actor to x, y.
        """
        old = self.cshape.center.copy()
        vec = eu.Vector2(int(x), int(y))
        self.position = vec
        self.cshape.center = vec
        self.b2body.position = pixels_to_tiles((vec.x, vec.y))
        #map(lambda hand: hand.attached_move(vec - old), self.hands)

    def push_task(self, task):
        self.actions[0].task_manager.push_task(task)

    def push_inst_task(self, task):
        self.actions[0].task_manager.push_instant_task(task)

    def on_ground_begin(self, fixture):
        self.ground_count += 1
        self.on_ground = True

    def on_ground_end(self, fixture):
        self.ground_count -= 1
        if self.ground_count == 0:
            self.on_ground = False

    def take_hit(self, hit):
        """
        Check with every Body_Part is Hit hit or not.
        """
        self.body.collide(hit)

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
Actor.register_event_type('on_activate_trigger')
Actor.register_event_type('on_take_damage')
Actor.register_event_type('on_death')


#TODO Прописать в скелете б2мир и юзер дату.
class Cool_Actor(movable_object.Movable_Object):

    """
    Работает со Skeleton в качестве тела.
    """

    is_event_handler = True

    def __init__(self, body, position=(0, 0)):
        img = image.SolidColorImagePattern((0, 0, 0, 0)).create_image(2, 2)
        self.body = body(self)
        super(Cool_Actor, self).__init__(img, position=position)
        self.add(self.body)

        self.state_machine = State_Machine(self)

        self.inventory = Inventory(self)
        print self.b2body.position, "AFTER"
        self.schedule(self.update)

    def on_enter(self):
        super(Cool_Actor, self).on_enter()
        self.schedule(self.state_machine.update)

    def on_exit(self):
        super(Cool_Actor, self).on_exit()
        self.unschedule(self.state_machine.update)

    @property
    def direction(self):
        return self.scale_x

    @direction.setter
    def direction(self, direction):
        self.scale_x = direction

    def move(self, direction):
        self.state_machine.move(direction)

    def crouch(self):
        self.state_machine.crouch()

    def setup_b2body(self):
        super(Cool_Actor, self).setup_b2body()
        pix_to_tile = pixels_to_tiles
        #rx, ry = pix_to_tile((5, 5))
        shape = b2.b2CircleShape(radius=3, pos=(0, 3))
        self.b2body.CreateFixture(b2.b2FixtureDef(shape=shape))
        self.b2body.fixtures[-1].filterData.categoryBits = B2SMTH | B2ACTOR

        # self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2EdgeShape(vertex1=(-rx, -ry), vertex2=(rx, -ry)),
        #                                           isSensor=True))
        # self.b2body.fixtures[-1].filterData.categoryBits = B2GNDSENS
        # self.b2body.fixtures[-1].filterData.maskBits = B2LEVEL | B2ACTOR
        # self.world.addEventHandler(self.b2body.fixtures[-1], self.on_ground_begin, self.on_ground_end)

    def on_ground_begin(self, fixture):
        self.ground_count += 1
        self.on_ground = True

    def on_ground_end(self, fixture):
        self.ground_count -= 1
        if self.ground_count == 0:
            self.on_ground = False

    def _set_position(self, p):
        #print "POSITION", p
        BatchableNode._set_position(self, p)
        self.body.position = p

    def _set_rotation(self, a):
        BatchableNode._set_rotation(self, a)
        self.body.rotation = a

    def _set_scale(self, s):
        BatchableNode._set_scale(self, s)
        self.body.scale = s

    def _set_scale_x(self, s):
        BatchableNode._set_scale_x(self, s)
        self.body.scale_x = s

    def _set_scale_y(self, s):
        BatchableNode._set_scale_y(self, s)
        self.body.scale_y = s

    def use_item(self, item_type, trigger, args):       # MAIN or SECONDARY
        if item_type is MAIN:
            item = self.inventory.main_item
        else:
            item = self.inventory.secondary_item

        if not item:
            return
        if trigger and not item.on_use and item.available:
            item.start_use(*args)
        elif trigger and item.on_use and item.available:
            item.continue_use(*args)
        elif not trigger and item.on_use and item.available:
            item.end_use(*args)

    def start_interact_with_item(self, item):
        if item and item.item_update:
            self.schedule(item.item_update)

    def stop_interact_with_item(self, item):
        if item and item.item_update:
            self.unschedule(item.item_update)

    def collide(self, other):
        other._collide_actor(self)

    def _collide_actor(self, other):
        coll.collide_actor_actor(self, other)

    def _collide_hit_zone(self, other):
        coll.collide_actor_hit_zone(self, other)

    def _collide_slash(self, other):
        coll.collide_actor_slash(self, other)

    def put_item(self, item):
        self.inventory.put_item(item)

    def open(self):
        self.inventory.open()

    def close(self):
        self.inventory.close()

    def destroy(self):
        """
        Remove Actor from level
        """
        if self.fight_group > 0:
            for armor in filter(lambda x: (x.attached is not None), self.body.body_parts):
                armor.attached.drop()
            self.fight_group = -1
            self.remove_action(self.actions[0])
            self.kill()
            self.dispatch_event('on_death', self)

    def transfer(self):
        self.inventory.transfer()
        super(Cool_Actor, self).transfer()
        self.ground_count = 0
        self.on_ground = True

    def move_to(self, x, y):
        """
        Place Actor to x, y.
        """
        vec = eu.Vector2(int(x), int(y))
        self.position = vec
        self.b2body.position = pixels_to_tiles((vec.x, vec.y))
        #map(lambda hand: hand.attached_move(vec - old), self.hands)

    def push_task(self, task):
        self.actions[0].task_manager.push_task(task)

    def push_inst_task(self, task):
        self.actions[0].task_manager.push_instant_task(task)

    def take_hit(self, hit):
        """
        Check with every Body_Part is Hit hit or not.
        """
        self.body.collide(hit)

    # def show_hitboxes(self):
    #     """
    #     Show hitboxes of every Body_Part
    #     """
    #     self.body.show_hitboxes()

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

    def set_position(self, position):
        #print "POPPP", position
        val = tiles_to_pixels(position)
        self.position = val
        #print self.b2body.position