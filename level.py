__author__ = 'Ecialo'

from collections import namedtuple

import cocos
from cocos import layer
from pyglet.window import key
from pyglet.window import mouse
from cocos import tiles
from cocos.director import director
import hud

from location import Location_Layer


class Keyboard_Handler(object):

    def __init__(self):
        self.keyboard = key.KeyStateHandler()

    def __getitem__(self, item):
        return self.keyboard[item]

    def __setitem__(self, key, value):
        self.keyboard[key] = value


class Mouse_Handler(object):

    def __init__(self):
        self.mouse = {'pos': (0, 0),
                      'd': (0, 0),
                      mouse.LEFT: False,
                      mouse.RIGHT: False,
                      mouse.MIDDLE: False}

    def __getitem__(self, item):
        return self.mouse[item]

    def __setitem__(self, key, value):
        self.mouse[key] = value


class Level(object):

    def __init__(self, start_position, locations):
        self.locations = locations
        self.x, self.y = start_position
        self.spawn_point = "start"
        self.hero = 'hero'
        self.keyboard = Keyboard_Handler()
        self.mouse = Mouse_Handler()
        self.scroller = layer.ScrollingManager()

    def run(self):
        director.run(self.load_location())

    def load_location(self):
        location = self.locations[self.x][self.y]
        if isinstance(location, str):
            return self.load_from_file_location(location)
        else:
            return self.reload_location(location)

    def load_from_file_location(self, filename):
        """
        Create scrollable Level from tmx map
        """
        #print "load", filename, "location"
        print "\n\n\n\n LOAD FRSH LEVEL"
        scroller = self.scroller
        data = tiles.load(filename)
        back = data['Background']
        force = data['Player Level']
        scripts = data['Scripts']
        player_layer = Location_Layer(scripts, force, scroller, self.keyboard, self.mouse)
        self.locations[self.x][self.y] = [force, back, player_layer]
        return self._create_location(force, back, player_layer)

    def reload_location(self, layers):
        print "\n\n\n\n RELOADED LEVEL"
        self._create_location(*layers)

    def _create_location(self, force, back, player_layer):
        print "LOAD LOCATION ON", self.x, self.y
        player_layer.connect(self)
        scene = cocos.scene.Scene()
        scroller = player_layer.scroller
        try:
            scroller.remove("background")
            scroller.remove("foreground")
            scroller.remove("level")
        except:
            pass
        spawn_point = self.spawn_point + "_entry"

        player_layer.prepare(spawn_point, self.hero)

        scroller.add(back, z=-1, name="background")
        scroller.add(force, z=0, name="foreground")
        scroller.add(player_layer, z=1, name="level")

        scene.add(scroller, z=0)
        scene.add(hud.HUD(player_layer), z=2)
        scene.add(player_layer.hero.inventory, z=2)
        return scene

    def change_location(self, direction, actor, location):
        print 'change', direction
        self.unload_location(location)
        self.hero = location.hero
        if direction == "right":
            self.x += 1
            self.spawn_point = "left"
        elif direction == "left":
            self.x -= 1
            self.spawn_point = "right"
        elif direction == "up":
            self.y += 1
            self.spawn_point = "bottom"
        else:
            self.y -= 1
            self.spawn_point = "top"
        director.replace(self.load_location())

    def unload_location(self, location):
        print "LOCATION", location.hero.parent
        location.hero.kill()
        location.actors.remove(location.hero)
        location.collman.clear()
        #print "STACK", location.hero._event_stack
        location.hero.remove_handlers(location)
        #print "CLEAR STACK", location.hero._event_stack
        location.disconnect(self)
        location.unschedule(location.update)
        #location.hero.actions[0].task_manager.clear_queue()
        #location.hero.launcher.pop_handlers()

    def printer(self, location):
        print "PRINTER", location


