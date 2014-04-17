__author__ = 'Ecialo'

#import cocos
from pyglet.event import EventDispatcher
from cocos import collision_model as cm
from cocos import euclid as eu
from cocos import layer
import Box2D as b2

import movable_object
import consts as con
from consts import TILE_SIZE
import collides as coll
from inventory import Inventory

consts = con.consts


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
                #print 1234
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
        #print missile
        self.dispatch_event('on_launch_missile', missile)

    def destroy_missile(self, missile):
        #print "LOLOLOLOLOLLOLOLOLOLOLOLOLO"
        self.dispatch_event('on_remove_missile', missile)
Launcher.register_event_type('on_launch_missile')
Launcher.register_event_type('on_remove_missile')


class Actor(movable_object.Movable_Object):

    is_event_handler = True

    def __init__(self, body):
        cshape = cm.AARectShape(eu.Vector2(0, 0), TILE_SIZE/2, body.img.height/2)
        super(Actor, self).__init__(body.img, cshape=cshape)

        self.fight_group = -1

        self.direction = 1

        self.hands = []
        self.owner = self
        self.body = body(self)
        self.launcher = Launcher(self)
        self.state = 'stand'
        self.inventory = Inventory(None, None, None, None, self)

        pix_to_tile = con.pixel_value_to_tiles_value
        rx, ry = pix_to_tile((cshape.rx, cshape.ry))
        self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(vertices=[(-rx, ry), (-rx, -ry+0.1),
                                                                                    (-rx+0.1, -ry), (rx-0.1, -ry),
                                                                                    (rx, -ry+0.1), (rx, ry)])))
        self.b2body.fixtures[-1].filterData.categoryBits = con.B2SMTH | con.B2ACTOR
        self.b2body.CreateFixture(b2.b2FixtureDef(shape=b2.b2EdgeShape(vertex1=(-rx, -ry), vertex2=(rx, -ry)),
                                                  isSensor=True))
        self.b2body.fixtures[-1].filterData.categoryBits = con.B2GNDSENS
        self.b2body.fixtures[-1].filterData.maskBits = con.B2LEVEL
        self.world.contactListener.addEventHandler(self.b2body.fixtures[-1], self.on_ground_begin, self.on_ground_end)
        self.ground_count = 0
        self.on_ground = False

        self.recovery = 0.0  # Time before moment when acton can be controlled again
        #self.scale = 0.5

        self.schedule(self.item_update)

    height = property(lambda self: self.body.img.height)
    width = property(lambda self: self.body.img.width)
    #attack_perform = property(lambda self: self.hands[0].attack_perform)

    def item_update(self, dt):
        map(lambda x: x.item_update(dt), self.hands)

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

    def refresh_environment(self, environment):
        map(lambda item: item(environment), self.hands)

    def get_item(self, item):
        self.inventory.get_item(item)

    def put_item(self, item):
        self.inventory.put_item(item)

    def open(self):
        self.inventory.open()

    def close(self):
        self.inventory.close()

    def change_weapon(self):
        self.inventory.change_weapon()

    def destroy(self):
        """
        Remove Actor from level
        """
        if self.fight_group > 0:
            for item in self.hands:
                item.drop()
            for armor in filter(lambda x: (x.attached is not None), self.body.body_parts):
                armor.attached.drop()
            self.fight_group = -1
            self.remove_action(self.actions[0])
            self.kill()
            self.dispatch_event('on_death', self)

    def _move(self, dx, dy):
        old = self.cshape.center.copy()
        super(Actor, self)._move(dx, dy)
        vec = self.cshape.center.copy() - old
        map(lambda hand: hand.attached_move(vec) if hand else not hand, self.hands)

    @activity
    def walk(self, horizontal_direction):
        """
        Move Actor in horizontal_direction with his body speed
        """
        if self.on_ground:
            d = horizontal_direction * self.body.speed
            #if abs(self.horizontal_speed + d) > self.body.speed:
            #self.push((d,0))
            self.b2body.linearVelocity.x = d
            #self.horizontal_speed = d
            if self.direction != horizontal_direction:
                self.turn()

    @activity
    def stand(self):
        """
        Do not move Actor
        """
        self.b2body.linearVelocity.x = 0
        #self.horizontal_speed = 0

    @activity
    def sit(self):
        self.b2body.linearVelocity.x = 0
        #self.horizontal_speed = 0

    def turn(self):
        self.direction = -self.direction
        self.body.turn()

    def push(self, v):
        self.b2body.linearVelocity += v
        #self.b2body.awake = True
        #self.b2body.ApplyLinearImpulse(impulse=v, point=self.b2body.position, wake=False)
        #self.horizontal_speed += v.x
        #self.vertical_speed += v.y

    #def get_item(self, item):
    #    if item.slot == con.HAND:
    #        self.hands.append(item)
    #        item.master = self
    #    else:
    #        for body_part in self.body.body_parts:
    #            if body_part.slot is item.slot:
    #                body_part.get_on(item)
    #                break

    @activity
    def jump(self):
        """
        Actor jump with his body jump speed.
        """
        #self.push((0,consts['params']['human']['jump_speed']))
        self.b2body.linearVelocity.y = consts['params']['human']['jump_speed']
        #self.vertical_speed = consts['params']['human']['jump_speed']

    def move_to(self, x, y):
        """
        Place Actor to x, y.
        """
        old = self.cshape.center.copy()
        vec = eu.Vector2(int(x), int(y))
        self.position = vec
        self.cshape.center = vec
        self.b2body.position = con.pixel_value_to_tiles_value((vec.x, vec.y))
        map(lambda hand: hand.attached_move(vec - old), self.hands)

    def choose_free_hand(self):
        for hand in self.hands:
            if not hand.on_use and hand.available:
                return hand
        return None

    def use_hand(self, hand, start_args=con.EMPTY_LIST,
                 continue_args=con.EMPTY_LIST,
                 end_args=con.EMPTY_LIST):
        hand.start_use(*start_args)
        hand.continue_use(*continue_args)
        hand.end_use(*end_args)

    def push_task(self, task):
        #print 123
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

    #def on_enter(self):
    #    self.launcher.push_handlers(self.get_ancestor(layer.scrolling.ScrollableLayer))
Actor.register_event_type('on_activate_trigger')
Actor.register_event_type('on_take_damage')
Actor.register_event_type('on_death')