__author__ = 'Ecialo'
from cocos.scene import Scene
from cocos import layer
from pyglet.window import key
from pyglet.window import mouse
from cocos import tiles
from cocos.director import director
import hud

from location import Location_Layer
from registry.utility import module_path_to_os_path


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

    def __init__(self, start_position, locations, path):
        path = module_path_to_os_path(path)
        self.locations = map(lambda nab: map(lambda location: path + location, nab), locations)
        self.x, self.y = start_position
        self.spawn_point = 'right'
        self.hero = 'Parzalon'
        self.keyboard = Keyboard_Handler()
        self.mouse = Mouse_Handler()
        self.scroller = layer.ScrollingManager()

    def run(self):
        director.push(self.load_location())

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
        scroller = self.scroller
        data = tiles.load(filename)
        back = data['Background']
        force = data['Player Level']
        scripts = data['Scripts']
        player_layer = Location_Layer(scripts, force, scroller, self.keyboard, self.mouse)
        self.locations[self.x][self.y] = [force, back, player_layer]
        return self._create_location(force, back, player_layer)

    def reload_location(self, layers):
        self._create_location(*layers)

    def _create_location(self, force, back, player_layer):
        player_layer.connect(self)
        scene = Scene()
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
        return scene

    def win(self, _, actor, location):
        self.unload_location(location)
        director.pop()

    def loose(self, location):
        self.unload_location(location)
        director.pop()

    def change_location(self, direction, actor, location):
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
        if location.hero.fight_group > 0:
            location.hero.kill()
            location.actors.remove(location.hero)
        location.unschedule(location.update)
        location.hero.remove_handlers(location)
        location.disconnect(self)

    def printer(self, location):
        print "PRINTER", location


