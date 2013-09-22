# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Ecialo"
__date__ ="$24.08.2013 12:54:13$"
import pyglet
from pyglet.window import key
from pyglet.window import mouse
consts = {'window': {'width': 800,
                     'height': 600,
                     'vsync': True,
                     'resizable': True,
                     'do_not_scale': True},
          'bindings': {'left': key.A,
                       'right': key.D,
                       'down': key.S,
                       'up': key.W,
                       'jump': key.SPACE,
                       'alt_mode': key.LSHIFT,
                       'first_hand': mouse.LEFT,
                       'second_hand': mouse.RIGHT},
          'color': {'white': (255, 255, 255, 255)},
          'img': {'human': pyglet.resource.image('chelovek_v2.png')},
          'params': {'human': {'speed': 200,
                               'jump_speed': 1000},
                     'primitive': {'range_of_vision': 400,
                                   'mastery': 0.05,
                                   'closest': 40}},
          'group': {'hero': 0,
                    'opponent': 1},
          'parry_cos_disp': 0.5,
          'effective_dst': 2.0/3.0,
          'test_slash_time': 0.8,
          'gravity': 1500,
          'rubbing': 100,
          'slash_fight_group': 100
         }

LEFT, UP, RIGHT, DOWN, NO_TR = 0b1000, 0b0100, 0b0010, 0b0001, 0b0000
CHOP, STAB = xrange(2)

if __name__ == "__main__":
    print "Hello World"
