__author__ = 'Ecialo'

from pyglet import event

from cocos import collision_model as cm
from cocos import layer

import Box2D as b2

import movable_object
import effects as eff
import actor as ac
import obj_db as db
import consts as con
import brains as br

consts = con.consts


def _spawn_unit(level, name, pos):
    #print "LOLOLO"
    un_par = db.objs[name]
    unit = ac.Actor(un_par['body'])
    map(lambda x: unit.get_item(x()(level)), un_par['items'])
    map(lambda x: unit.put_item(x()(level)), un_par['items'])
    unit.move_to(*pos)
    if un_par['brain'].fight_group is consts['group']['hero'] and level.hero is None:
        level.hero = unit
    elif un_par['brain'].fight_group is consts['group']['hero'] and level.hero is not None:
        level.hero.destroy()
        level.hero = unit
    unit.launcher.push_handlers(level)
    level.actors.append(unit)
    level.add(unit, z=2)
    unit.do(un_par['brain']())


def _spawn_prepared_unit(level, unit, pos):
    print "spawn_prepared"
    unit.move_to(*pos)
    unit.launcher.push_handlers(level)
    level.actors.append(unit)
    level.add(unit, z=2)
    action = unit.actions[0]
    unit.actions.pop()
    unit.do(type(action)())


class Script_Manager(event.EventDispatcher):

    def activate_trigger(self, tr, actor, location):
        #print "LOLOLOLOLOLOLOLOLOLOOOOLOLOL", location
        tr_name = tr.properties['trigger']
        tr_attr = tr.properties[tr_name]
        self.dispatch_event(tr_name, tr_attr, actor, location)
        self.dispatch_event('printer', location)
        actor.last_activated_trigger = None

    def activate_event(self, ev, actor, location):
        ev_name = ev.properties['event']
        ev_attr = ev.properties[ev_name]
        self.dispatch_event(ev_name, ev_attr, actor, location)

Script_Manager.register_event_type('change_location')
Script_Manager.register_event_type('run_dialog')
Script_Manager.register_event_type('printer')
Script_Manager.register_event_type('loose')
Script_Manager.register_event_type('win')


class b2Listener(b2.b2ContactListener):
    def __init__(self):
        b2.b2ContactListener.__init__(self)
    def BeginContact(self, contact):
        fa = contact.fixtureA
        fb = contact.fixtureB
        sa = fa.sensor
        sb = fb.sensor
        if sa or sb:
            if sb:
                sensor = fb
                other = fa
            else:
                sensor = fa
                other = fb
            sensor.body.userData.ground_count += 1
            sensor.body.userData.on_ground = True

    def EndContact(self, contact):
        fa = contact.fixtureA
        fb = contact.fixtureB
        sa = fa.sensor
        sb = fb.sensor
        if sa or sb:
            if sb:
                sensor = fb
                other = fa
            else:
                sensor = fa
                other = fb
            sensor.body.userData.ground_count -= 1
            if sensor.body.userData.ground_count == 0:
                sensor.body.userData.on_ground = False
    def PreSolve(self, contact, oldManifold):
        pass
    def PostSolve(self, contact, impulse):
        pass


class Location_Layer(layer.ScrollableLayer):

    is_event_handler = True

    _spawn = {con.UNIT: _spawn_unit}

    def __init__(self, scripts, force_ground, scroller, keyboard, mouse):
        super(Location_Layer, self).__init__()

        self.loc_mouse_handler = mouse
        self.loc_key_handler = keyboard

        #Tilemaps. Setup this on Actor.
        self.scroller = scroller
        self.force_ground = force_ground
        #self.scripts = scripts

        #Box2D world
        self.b2world = b2.b2World(gravity=(0, -100),#-con.tiles_value_to_pixel_value(con.GRAVITY)),
                                  contactListener=b2Listener())
        self.b2level = self.b2world.CreateStaticBody()
        self._create_b2_tile_map(force_ground)
        #print self.b2world

        #Collision managers. For static global and dynamic screen objects
        self.script_manager = Script_Manager()
        self.script_manager.push_handlers(self)

        self.scripts = cm.CollisionManagerBruteForce()
        self.collman = cm.CollisionManagerBruteForce()
        self.static_collman = cm.CollisionManagerBruteForce()

        for sc in scripts:
            self.scripts.add(sc)

        #Lists of dynamic objs
        self.hits = []
        self.missiles = []
        self.actors = []

        #Append hero
        self.hero = None

    def connect(self, level):
        #self.script_manager.push_handlers(level)
        self.script_manager.push_handlers(level)
        #print "EVENT STACK", self.script_manager._event_stack

    def disconnect(self, level):
        self.script_manager.pop_handlers()
        #print "NEW EVENT STACK", self.script_manager._event_stack

    def prepare(self, spawn_point, hero):
        #print spawn_point, hero
        movable_object.Movable_Object.tilemap = self.force_ground
        movable_object.Movable_Object.world = self.b2world
        #print "ZEBRA"
        br.Task.environment = self.force_ground
        eff.Advanced_Emitter.surface = self  # This bad
        #self.loc_key_handler
        for sc in self.scripts.known_objs():
            if spawn_point in sc.properties:
                #r = self.hero.get_rect()
                #r.midbottom = sc.midbottom
                print hero
                dx, dy = sc.center
                self.spawn(hero, (dx, dy))
                #print "LOSHADKA"
        if hero is not 'hero':
            self.hero = hero
        print "Prepared"
        #print self.hero._event_stack
        self.hero.push_handlers(self)
        self.hero.refresh_environment(self)
        self.hero.show_hitboxes()
        print self.scroller
        for sc in self.scripts.known_objs():
            if 'spawn' in sc.properties:
                #r = self.opponent.get_rect()
                #r.midbottom = sc.midbottom
                dx, dy = sc.center
                self.spawn(sc.properties['spawn'], (dx, dy))
        self.run()
        #self.scroller.set_focus(*self.hero.position)

    def _create_b2_tile_map(self, rect_map):
        WIDTH, HEIGHT = con.TILE_SIZE/2, con.TILE_SIZE/2
        cells = rect_map.cells

        shape = b2.b2PolygonShape()
        #print "TEST"
        i = 0
        for cell_column in cells:
            for cell in cell_column:
                if cell.get('top'):
                    #print i
                    i += 1
                    #print self.b2world
                    shape.SetAsBox(WIDTH, HEIGHT, cell.center, 0)
                    self.b2level.CreateFixture(shape=shape, userData=cell)
                    #if i>9990:
                    #   temp = self.b2world
        #print "TEST21"

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
        for hit in self.hits:
            if hit.uncompleteness() <= 0.01 and not hit.completed:
                print "hit complete"
                hit.complete()
            elif hit.completed:
                pass
            else:
                hit.time_to_complete = hit.time_to_complete - dt
                self.collman.add(hit)

        for missile in self.missiles:
            #print missile.uncompleteness(), missile.completed
            if missile.uncompleteness() <= 0.01 and not missile.completed:
                missile.complete()
            elif missile.completed:
                pass
            else:
                self.collman.add(missile)

        for hit_1, hit_2 in self.collman.iter_all_collisions():
            hit_1.collide(hit_2)
        #if self.hero.fight_group > 0:
        #    self.collman.add(self.hero)
        map(self._actor_kick_or_add, self.actors)

        for obj1, obj2 in self.collman.iter_all_collisions():
            obj1.collide(obj2)

    def spawn(self, obj, pos):
        if obj in db.objs:
            #print "SLONIK"
            self._spawn[db.objs[obj]['type']](self, obj, pos)
        elif isinstance(obj, ac.Actor):
            #print "ZIRAFIK"
            _spawn_prepared_unit(self, obj, pos)

    def on_launch_missile(self, missile):
        self.add(missile, z=2)
        self.missiles.append(missile)

    def on_remove_missile(self, missile):
       #print missile
        self.missiles.remove(missile)
        #if self.collman.knows(missile):
        #    self.collman.remove_tricky(missile)
        missile.kill()

    def on_activate_trigger(self, trigger, actor):
        print "!!!!"
        print "location triggered"
        print "!!!!"
        self.script_manager.activate_trigger(trigger, actor, self)

    def on_death(self, actor):
        self.script_manager.dispatch_event('loose', self)

    def on_do_hit(self, hit):
        """
        Callback from Weapon. Append Hit to Level for show.
        """
        self.add(hit, z=3)
        print "Recieve hit to append", hit
        #hit.do(FlipY3D())

    def on_perform_hit(self, hit):
        """
        Callback from Weapon. Append Hit to collision manager for calculate collisions
        """
        #print hit.master.master.fight_group
        print "append hit to collision manager", hit
        self.hits.append(hit)

    def on_remove_hit(self, hit):
        """
        Remove overdue Hit from game.
        """
        try:
            self.hits.remove(hit)
        except ValueError:
            pass
        print "remove hit"

    def on_drop_item(self, item):
        #print item
        self.add(item, z=3)

    def on_get_up_item(self, item):
        self.static_collman.remove_tricky(item)
        item.kill()

    def on_lay_item(self, item):
        self.static_collman.add(item)

    def on_mouse_motion(self, x, y, dx, dy):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler['d'] = (dx, dy)
        #self.scroller.set_focus(*self.loc_mouse_handler['pos'])

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
        #print symbol
        self.loc_key_handler[symbol] = True

    def on_key_release(self, symbol, modifers):
        self.loc_key_handler[symbol] = False
        #print id(self.loc_key_handler)
        #if symbol == key.SPACE:
        #    self.remove(self.hero)

