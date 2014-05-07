# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"
__date__ = "$24.08.2013 12:54:13$"
from os import path
import pyglet
from pyglet.window import key
from pyglet.window import mouse
from math import sqrt


TILE_SIZE = 32
GRAVITY = 50


def tiles_value_to_pixel_value(tiles):
    #return float(tiles*TILE_SIZE)
    if hasattr(tiles, '__iter__'):
        return type(tiles)([tiles_value_to_pixel_value(x) for x in tiles])
    else:
        return tiles*1.0*TILE_SIZE

tile_to_pix = tiles_value_to_pixel_value

def pixel_value_to_tiles_value(pixels):
    if hasattr(pixels, '__iter__'):
        return type(pixels)([pixel_value_to_tiles_value(x) for x in pixels])
    else:
        return pixels*1.0/TILE_SIZE

pix_to_tile = pixel_value_to_tiles_value

def jump_height_to_pixel_speed(height_in_tiles):
    return sqrt(2*GRAVITY*height_in_tiles)


def binary_list(n):
    if n >= 16:
        return []
    return map(lambda x: 2**x, range(n))

consts = {'window': {'width': 800,
                     'height': 600,
                     'vsync': True,
                     'resizable': True,
                     'do_not_scale': True},
          'bindings': {'left': key.A,
                       'right': key.D,
                       'down': key.S,
                       'up': key.W,
                       'action': key.F,
                       'gain': key.G,
                       'inventory': key.I,
                       'jump': key.SPACE,
                       'alt_mode': key.LSHIFT,
                       'first_hand': mouse.LEFT,
                       'second_hand': mouse.RIGHT,
                       'change_weapon': key.R},
          'color': {'white': (255, 255, 255, 255)},
          'img': {'hero': pyglet.resource.image('stand.png'),
                  'hero_sit': pyglet.resource.image('stand.png'),
                  'human': pyglet.resource.image('stand.png'),
                  'human_sit': pyglet.resource.image('sit.png'),
                  'weapon': pyglet.resource.image('sword.png'),
                  'knife': pyglet.resource.image('knife.png'),
                  'bullet': pyglet.resource.image('bullet.png'),
                  'rifle': pyglet.resource.image('fuzeja.png'),
                  'helmet': pyglet.resource.image('helm.png'),
                  'twister': pyglet.resource.image('twister.png'),
                  'inventory': pyglet.resource.image('inventory.png'),
                  'skull': pyglet.resource.image('skull.png'),
                  'shard': pyglet.resource.image('twister_shard.png')},
          'hud': {'body': {'back':   {'head': pyglet.resource.image('ui_head_back.png'),
                                      'chest': pyglet.resource.image('ui_chest_back.png'),
                                      'left_arm': pyglet.resource.image('ui_left_arm_back.png'),
                                      'right_arm': pyglet.resource.image('ui_right_arm_back.png'),
                                      'legs': pyglet.resource.image('ui_legs_back.png')},
                           'front':   {'head': pyglet.resource.image('ui_head_front.png'),
                                       'chest': pyglet.resource.image('ui_chest_front.png'),
                                       'left_arm': pyglet.resource.image('ui_left_arm_front.png'),
                                       'right_arm': pyglet.resource.image('ui_right_arm_front.png'),
                                       'legs': pyglet.resource.image('ui_legs_front.png')},
                           'armored': {'head': pyglet.resource.image('ui_head_armored.png'),
                                       'chest': pyglet.resource.image('ui_chest_armored.png'),
                                       'left_arm': pyglet.resource.image('ui_left_arm_armored.png'),
                                       'right_arm': pyglet.resource.image('ui_right_arm_armored.png'),
                                       'legs': pyglet.resource.image('ui_legs_armored.png')}
                           },
                  'status': {'health_icon': pyglet.resource.image('ui_health_icon.png')},
                  },
          'params': {'human': {'speed': 7,
                               'jump_speed': jump_height_to_pixel_speed(4)},
                     'primitive': {'range_of_vision': tiles_value_to_pixel_value(15),
                                   'mastery': 0.05,
                                   'closest': 40}},
          'group': {'hero': 1,
                    'opponent': 2},
          'portrait': {'parzalon': pyglet.resource.image('parzalon_portrait.png'),
                       'enemy': pyglet.resource.image('enemy_portrait.jpg')},
          'parry_cos_disp': 0.5,
          'effective_dst': 4.0/3.0,
          'test_slash_time': 0.8,
          'gravity': GRAVITY,
          'rubbing': 3,
          'tile_size': 32,
          'slash_fight_group': 100,
          'missile_fight_group': 1000,
          'animation_frames': {'walk': ('2.png', '3.png')}
          }

LEFT, UP, RIGHT, DOWN, NO_TR = 0b1000, 0b0100, 0b0010, 0b0001, 0b0000
FIRST_HAND, SECOND_HAND = xrange(2)
FIRST, SECOND = xrange(2)
HAND, HEAD, CHEST, LEGS = xrange(4)
ARMOR = 100
CHOP, STAB, CLEAVE, PENETRATE = xrange(4)
LINE, RECTANGLE = xrange(2)
UNIT, ITEM = xrange(2)
EMPTY_LIST = []
B2SMTH, B2LEVEL, B2GNDSENS, B2HITZONE, B2ACTOR, B2SWING , B2BODYPART, B2ITEM = binary_list(8)
B2NONE = 0x0000
B2EVERY = 0xFFFF
