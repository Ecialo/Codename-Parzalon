import task
import effects as eff

__author__ = 'Ecialo'

from collections import deque

from pyglet import event

from cocos import collision_model as cm
from cocos import layer

import Box2D as b2

from script_manager import Script_Manager
import movable_object
import actor as ac

from registry.Units import units_base
from registry.group import HERO, UNIT
from registry.box2d import *

def _spawn_unit(level, name, pos):
    un_par = units_base[name]
    unit = ac.Actor(un_par['body'])
    map(lambda x: unit.put_item(x()(level)), un_par['items'])
    unit.move_to(*pos)
    if un_par['brain'].fight_group is HERO and level.hero is None:
        level.hero = unit
    elif un_par['brain'].fight_group is HERO and level.hero is not None:
        level.hero.destroy()
        level.hero = unit
    unit.launcher.push_handlers(level)
    level.actors.append(unit)
    level.add(unit, z=2)
    unit.do(un_par['brain']())


def _spawn_prepared_unit(level, unit, pos):
    unit.transfer()
    unit.move_to(*pos)
    unit.launcher.push_handlers(level)
    level.actors.append(unit)
    level.add(unit, z=2)
    action = unit.actions[0]
    unit.actions.pop()
    unit.do(type(action)())


# class Script_Manager(event.EventDispatcher):
#
#     def activate_trigger(self, tr, actor, location):
#         tr_name = tr.properties['trigger']
#         tr_attr = tr.properties[tr_name]
#         self.dispatch_event(tr_name, tr_attr, actor, location)
#         self.dispatch_event('printer', location)
#         actor.last_activated_trigger = None
#
#     def activate_event(self, ev, actor, location):
#         ev_name = ev.properties['event']
#         ev_attr = ev.properties[ev_name]
#         self.dispatch_event(ev_name, ev_attr, actor, location)
#
# Script_Manager.register_event_type('change_location')
# Script_Manager.register_event_type('run_dialog')
# Script_Manager.register_event_type('printer')
# Script_Manager.register_event_type('loose')
# Script_Manager.register_event_type('win')


class b2Listener(b2.b2ContactListener):
    def __init__(self):
        b2.b2ContactListener.__init__(self)
        self.beginHandlers = {}
        self.endHandlers = {}

    def BeginContact(self, contact):
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB
        try:
            self.beginHandlers[fixtureA](fixtureB)
        except KeyError:
            pass
        try:
            self.beginHandlers[fixtureB](fixtureA)
        except KeyError:
            pass

    def EndContact(self, contact):
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB
        try:
            self.endHandlers[fixtureA](fixtureB)
        except KeyError:
            pass
        try:
            self.endHandlers[fixtureB](fixtureA)
        except KeyError:
            pass

    def PreSolve(self, contact, oldManifold):
        pass

    def PostSolve(self, contact, impulse):
        pass

    def addEventHandler(self, listener, beginHandler, endHandler):
        self.beginHandlers[listener] = beginHandler
        self.endHandlers[listener] = endHandler

    def removeEventHandler(self, listener):
        del self.beginHandlers[listener]
        del self.endHandlers[listener]

    def getHandlers(self, listener):
        if listener in self.beginHandlers:
            return (self.beginHandlers[listener], self.endHandlers[listener])
        else:
            return None


class Fake_Filter_Data(object):

    def __init__(self):
        self._data = {}
        del self._data['_data']

    def __setattr__(self, key, value):
        super(Fake_Filter_Data, self).__setattr__(key, value)
        self._data[key] = value


class Fake_Fixture(object):

    def __init__(self, fixture_def):
        self.fixture_def = fixture_def
        self.filterData = Fake_Filter_Data()
        self.true_fixture = None


class Fake_Dynamic_Body(object):

    def __init__(self, **kwargs):
        self._data = {}
        self.kwargs = kwargs
        self.fixtures = []
        for key, value in kwargs.iteritems():
            self.__setattr__(key, value)
        del self._data['_data']
        del self._data['kwargs']
        del self._data['fixtures']

    def CreateFixture(self, fixture_def):
        fixture = Fake_Fixture(fixture_def)
        self.fixtures.append(fixture)
        return fixture

    def __setattr__(self, key, value):
        super(Fake_Dynamic_Body, self).__setattr__(key, value)
        self._data[key] = value


class Cool_B2_World(b2.b2World):

    def __init__(self, *args, **kwargs):
        self.true_listener = kwargs['contactListener']
        super(Cool_B2_World, self).__init__(*args, **kwargs)
        self.fixtures_to_destroy = deque()
        self.bodies_to_destroy = deque()
        self.bodies_to_create = deque()
        self.to_listener = deque()

    def CreateDynamicBody(self, **kwargs):
        fake_body = Fake_Dynamic_Body(**kwargs)
        self.bodies_to_create.append(fake_body)
        return fake_body

    def _create_dynamic_body(self, fake_body):
        body = super(Cool_B2_World, self).CreateDynamicBody(**fake_body.kwargs)
        body.cool_world = self
        for attr_name, attr_value in fake_body._data.iteritems():
            body.__setattr__(attr_name, attr_value)
        for fake_fixture in fake_body.fixtures:
            new_fixture = body.CreateFixture(fake_fixture.fixture_def)
            for attr_name, attr_value in fake_fixture.filterData._data.iteritems():
                new_fixture.filterData.__setattr__(attr_name, attr_value)
            fake_fixture.true_fixture = new_fixture
            user = new_fixture.userData
            if hasattr(user, "b2fixture"):
                user.b2fixture = new_fixture
        user = fake_body.userData
        user.b2body = body

    def destroy_fixture(self, fixture):
        self.fixtures_to_destroy.append(fixture)

    def destroy_body(self, body):
        self.bodies_to_destroy.append(body)

    def addEventHandler(self, listener, beginHandler, endHandler):
        if isinstance(listener, Fake_Fixture):
            self.to_listener.append((listener, beginHandler, endHandler))
        else:
            self.contactListener.addEventHandler(listener, beginHandler, endHandler)

    def Step(self, *args, **kwargs):
        fixtures_to_destroy = self.fixtures_to_destroy
        while fixtures_to_destroy:
            fixture = fixtures_to_destroy.popleft()
            fixture.body.DestroyFixture(fixture)

        bodies_to_destroy = self.bodies_to_destroy
        while bodies_to_destroy:
            body = bodies_to_destroy.popleft()
            self.DestroyBody(body)

        bodies_to_create = self.bodies_to_create
        while bodies_to_create:
            fake_body = bodies_to_create.popleft()
            self._create_dynamic_body(fake_body)

        rest = []
        to_listener = self.to_listener
        while to_listener:
            handler = to_listener.popleft()
            true_fixture = handler[0].true_fixture
            if true_fixture:
                self.contactListener.addEventHandler(true_fixture, handler[1], handler[2])
            else:
                rest.append(handler)
        self.to_listener.extend(rest)
        super(Cool_B2_World, self).Step(*args, **kwargs)


class Location_Layer(layer.ScrollableLayer):

    is_event_handler = True

    _spawn = {UNIT: _spawn_unit}

    def __init__(self, scripts, force_ground, scroller, keyboard, mouse):
        super(Location_Layer, self).__init__()

        self.loc_mouse_handler = mouse
        self.loc_key_handler = keyboard

        #Tilemaps. Setup this on Actor.
        self.scroller = scroller
        self.force_ground = force_ground

        #Box2D world
        self.b2world = Cool_B2_World(gravity=(0, -GRAVITY),
                                     contactListener=b2Listener())
        self.b2level = self.b2world.CreateStaticBody()
        self._create_b2_tile_map(force_ground)

        #self.script_manager.push_handlers(self)

        #Lists of dynamic objs
        self.hits = []
        self.missiles = []
        self.actors = []

        #Append hero
        self.hero = None

        self.script_manager = Script_Manager(scripts, self)

    def get_script_by_name(self, name):
        return self.script_manager.get_script_by_name(name)

    def connect(self, level):
        #self.script_manager.push_handlers(level)
        pass

    def disconnect(self, level):
        #self.script_manager.pop_handlers()
        pass

    def prepare(self, spawn_point, hero):
        movable_object.Movable_Object.tilemap = self.force_ground
        movable_object.Movable_Object.world = self.b2world
        movable_object.Movable_Object.location = self
        self.b2world.contactListener = self.b2world.true_listener
        task.environment = self.force_ground
        eff.Advanced_Emitter.surface = self  # This bad
        self.hero.push_handlers(self)
        #self.hero.refresh_environment(self)
        #self.hero.show_hitboxes()
        self.run()

    def _create_b2_tile_map(self, rect_map):

        def try_create_and_append_block(cells_in_block, mode):
            if cells_in_block and mode == 0:
                cells_in_block.pop()
            if cells_in_block:
                height = len(cells_in_block) if not mode else 1
                width = len(cells_in_block) if mode else 1
                half_height = height/2.0
                half_width = width/2.0
                lowest_cell = cells_in_block[0]
                cx = lowest_cell.i + half_width
                cy = lowest_cell.j + half_height
                shape.SetAsBox(half_width, half_height, (cx, cy), NO_ROTATION)
                self.b2level.CreateFixture(shape=shape, userData=cell)
                self.b2level.fixtures[-1].filterData.categoryBits = B2SMTH | B2LEVEL
                self.b2level.fixtures[-1].filterData.maskBits = B2EVERY

        cells = rect_map.cells
        m = len(cells)
        n = len(cells[0])

        shape = b2.b2PolygonShape()
        for cell_column in cells:
            cells_in_vertical_block = []
            for cell in cell_column:
                if cell.get('top'):
                    cells_in_vertical_block.append(cell)
                else:
                    try_create_and_append_block(cells_in_vertical_block, 0)
                    cells_in_vertical_block = []
            try_create_and_append_block(cells_in_vertical_block, 0)

        for j in xrange(n):
            cells_in_horizontal_block = []
            for i in xrange(m):
                cell = cells[i][j]
                if cell.get('top'):
                    cells_in_horizontal_block.append(cell)
                else:
                    try_create_and_append_block(cells_in_horizontal_block, 1)
                    cells_in_horizontal_block = []
            try_create_and_append_block(cells_in_horizontal_block, 1)

    def run(self):
        self.schedule(self.update)

    def _actor_kick_or_add(self, actor):
        """
        Remove Actor from self if he is dead
        """
        if actor.fight_group >= 0:
            self.collman.add(actor)
        else:
            self.actors.remove(actor)

    def update(self, dt):

        """
        1)Update Hits in dynamic collision manager and remove overdue objects
        2)Check all collisions between Hits
        3)Update Actors in collisions managers and remove dead Actors
        4)Check all collisions between Actors and immovable objects
        5)Check all collisions between all dynamic objects
        """

        #All collisions between movable objects calculate here
        events = filter(lambda sc: 'event' in sc.properties,
                              self.scripts.iter_colliding(self.hero))
        for ev in events:
            self.script_manager.activate_event(ev, self.hero, self)
            self.scripts.remove_tricky(ev)

        self.b2world.Step(dt, 1, 1)
        self.collman.clear()

        for missile in self.missiles:
            if missile.uncompleteness() <= 0.01 and not missile.completed:
                missile.complete()
            elif missile.completed:
                pass
            else:
                self.collman.add(missile)
        map(self._actor_kick_or_add, self.actors)

    def spawn(self, obj, pos):
        if obj in units_base:
            self._spawn[0](self, obj, pos)
        elif isinstance(obj, ac.Actor):
            _spawn_prepared_unit(self, obj, pos)

    def on_launch_missile(self, missile):
        self.add(missile, z=2)
        self.missiles.append(missile)

    def on_remove_missile(self, missile):
        self.missiles.remove(missile)
        missile.kill()

    def on_activate_trigger(self, trigger, actor):
        self.script_manager.activate_trigger(trigger, actor, self)

    def on_death(self, actor):
        self.script_manager.dispatch_event('loose', self)

    def on_do_hit(self, hit):
        """
        Callback from Weapon. Append Hit to Level for show.
        """
        self.add(hit, z=3)

    def on_perform_hit(self, hit):
        """
        Callback from Weapon. Append Hit to collision manager for calculate collisions
        """
        self.hits.append(hit)

    def on_drop_item(self, item):
        self.add(item, z=3)

    def on_get_up_item(self, item):
        self.static_collman.remove_tricky(item)
        item.kill()

    def on_lay_item(self, item):
        self.static_collman.add(item)

    def on_mouse_motion(self, x, y, dx, dy):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler['d'] = (dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler['d'] = (dx, dy)

    def on_mouse_press(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler[buttons] = True

    def on_mouse_release(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler[buttons] = False

    def on_key_press(self, symbol, modifers):
        self.loc_key_handler[symbol] = True

    def on_key_release(self, symbol, modifers):
        self.loc_key_handler[symbol] = False


