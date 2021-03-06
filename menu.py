__author__ = 'Shiz0'

from cocos.menu import *
from cocos.layer import MultiplexLayer
from cocos.scene import Scene
from cocos.director import director
from pyglet import app

from registry.Levels import levels_base


class GameMenu(Menu):
    def __init__(self):
        super(GameMenu, self).__init__()
        self.scene = Scene()
        self.scene.add(MultiplexLayer(MainMenu(),
                                      OptionsMenu(),
                                      KeyBindingMenu()), z=1)

    def start_game(self):
        director.run(self.scene)


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__(title='Black Pact')

        self.menu_anchor_y = CENTER
        self.menu_anchor_x = CENTER

        self.items = []
        self.items.append(MenuItem('New Game', self.on_new_game))
        self.items.append(MenuItem('Options', self.on_options_enter))
        self.items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(self.items, shake(), shake_back())

    def on_new_game(self):
        lvl = levels_base['Test_Level']
        lvl.run()

    def on_options_enter(self):
        self.parent.switch_to(1)

    def on_quit(self):
        app.exit()


class OptionsMenu(Menu):
    def __init__(self):
        super(OptionsMenu, self).__init__('Options')

        self.menu_anchor_y = CENTER
        self.menu_anchor_x = CENTER

        self.items = []
        self.items.append(MenuItem('Change controls', self.on_change_controls))
        self.items.append(ToggleMenuItem('Show FPS: ', self.on_show_FPS, director.show_FPS))
        self.items.append(MenuItem('Back', self.on_quit))

        self.create_menu(self.items, shake(), shake_back())

    def on_change_controls(self):
        self.parent.switch_to(2)

    def on_show_FPS(self, state):
        director.show_FPS = state

    def on_quit(self):
        self.parent.switch_to(0)


class KeyBindingMenu(Menu):
    def __init__(self):
        super(KeyBindingMenu, self).__init__('Key binding')

        self.menu_anchor_y = CENTER
        self.menu_anchor_x = CENTER

        self.items = []
        self.items.append(MenuItem('Back', self.on_quit))

        self.create_menu(self.items, shake(), shake_back())

    def on_quit(self):
        self.parent.switch_to(1)