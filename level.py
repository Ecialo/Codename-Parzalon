__author__ = 'Ecialo'

#import pyglet
from pyglet.window import key
from pyglet.window import mouse

import cocos
from cocos.director import director
from cocos import collision_model as cm
from cocos import layer
from cocos import tiles

import movable_object
import effects as eff
import bodies as bd
import weapons as wp
import armors as ar
import brains as br
import actor as ac
import obj_db as db
import consts as con
from inventory import Inventory

consts = con.consts


def _spawn_unit(level, name, pos):
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


class Level_Layer(layer.ScrollableLayer):

    is_event_handler = True

    _spawn = {con.UNIT: _spawn_unit}

    def __init__(self, scripts, force_ground, scroller):
        super(Level_Layer, self).__init__()

        #Controller
        self.loc_mouse_handler = {'pos': (0, 0),
                                  'd': (0, 0),
                                  mouse.LEFT: False,
                                  mouse.RIGHT: False,
                                  mouse.MIDDLE: False}

        self.loc_key_handler = key.KeyStateHandler()
        director.window.push_handlers(self.loc_key_handler)

        #Tilemaps. Setup this on Actor.
        self.scroller = scroller
        self.force_ground = force_ground
        movable_object.Movable_Object.tilemap = force_ground  # This bad

        #Setup layer for effects
        eff.Advanced_Emitter.surface = self  # This bad

        #Collision managers. For static global and dynamic screen objects
        self.collman = cm.CollisionManagerBruteForce()
        self.static_collman = cm.CollisionManagerBruteForce()

        #Lists of dynamic objs
        self.hits = []
        self.missiles = []
        self.actors = []

        #Append ground
        #self.add(force_ground, z = 1)

        #Append hero
        self.hero = None
        #self.hero.get_item(wp.Sword()(self))
        #for i in xrange(20):
        #    self.hero.get_item(wp.Knife()(self))
        #self.hero.get_item(wp.Musket()(self))
        #self.hero.get_item(ar.Helmet())
        #self.hero.weapon.push_handlers(self)
        #self.hero.move(200, 200)
        #self.add(self.hero, z=2)

        #Append opponent
        #self.opponent = ac.Actor(bd.Human)
        #self.opponent.get_item(wp.Sword()(self))
        #self.opponent.get_item(ar.Helmet()(self))
        #self.opponent.get_item(wp.Empty_Hand(self), 1)
        #self.opponent.weapon.push_handlers(self)
        #self.opponent.move(400, 200)
        #self.add(self.opponent, z=2)
        #self.actors.append(self.opponent)

        #Move guys to location
        for sc in scripts:
            if 'player' in sc.properties:
                #r = self.hero.get_rect()
                #r.midbottom = sc.midbottom
                dx, dy = sc.center
                self.spawn('hero', (dx, dy))
            elif 'opponent' in sc.properties:
                #r = self.opponent.get_rect()
                #r.midbottom = sc.midbottom
                dx, dy = sc.center
                self.spawn('enemy', (dx, dy))

        #Set up brains
        #self.opponent.do(br.Primitive_AI())
        #self.opponent.do(br.Dummy())
        #self.hero.do(br.Controller())

        self.hero.show_hitboxes()
        self.actors[0].show_hitboxes()

        #Run
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
        self.collman.clear()
        for hit in self.hits:
            if hit.time_to_complete <= 0.0 and not hit.completed:
                hit.complete()
            elif hit.completed:
                pass
            else:
                hit.time_to_complete = hit.time_to_complete - dt
                self.collman.add(hit)

        for missile in self.missiles:
            self.collman.add(missile)

        for hit_1, hit_2 in self.collman.iter_all_collisions():
            hit_1.collide(hit_2)
        #if self.hero.fight_group > 0:
        #    self.collman.add(self.hero)
        map(self._actor_kick_or_add, self.actors)

        for obj1, obj2 in self.collman.iter_all_collisions():
            obj1.collide(obj2)

    def spawn(self, obj_name, pos):
        if obj_name in db.objs:
            self._spawn[db.objs[obj_name]['type']](self, obj_name, pos)

    def on_launch_missile(self, missile):
        self.add(missile, z=2)
        self.missiles.append(missile)

    def on_remove_missile(self, missile):
        #print missile
        self.missiles.remove(missile)
        #if self.collman.knows(missile):
        #    self.collman.remove_tricky(missile)
        missile.kill()

    def on_do_hit(self, hit):
        """
        Callback from Weapon. Append Hit to Level for show.
        """
        self.add(hit, z=2)

    def on_perform_hit(self, hit):
        """
        Callback from Weapon. Append Hit to collision manager for calculate collisions
        """
        #print hit.master.master.fight_group
        self.hits.append(hit)

    def on_remove_hit(self, hit):
        """
        Remove overdue Hit from game.
        """
        self.hits.remove(hit)
        hit.kill()

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

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler['d'] = (dx, dy)

    def on_mouse_press(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler[buttons] = True

    def on_mouse_release(self, x, y, buttons, modifers):
        self.loc_mouse_handler['pos'] = self.scroller.pixel_from_screen(x, y)
        self.loc_mouse_handler[buttons] = False


def create_level(filename):

    """
    Create scrollable Level from tmx map
    """

    scene = cocos.scene.Scene()

    data = tiles.load(filename)
    back = data['Background']
    force = data['Player Level']
    scripts = data['Scripts']

    scroller = layer.ScrollingManager()
    player_layer = Level_Layer(scripts, force, scroller)
    #inventory = Inventory()

    scroller.add(back, z=-1)
    scroller.add(force, z=0)
    scroller.add(player_layer, z=1)

    #scene.add(inventory, z=2)
    scene.add(scroller, z=1)
    #inventory.open()
    #inventory.close()
    return scene