# -*- coding: utf-8 -*-

"""
Это реестр используемых игрой "постоянных".

В словарях хранится то, что должно поддаваться настройке из игры(например управление).
Это упростит дальнейший переход на shelve.

Основная единица измерения - тайл. Но так как движок использует пиксели,
здесь так же находятся функции пересчёта

Все данные разбиты по блокам

Постоянные нельзя объявлять где-либо, кроме этого реестра. Исключение: самодостаточные модули
коими должны вскоре стать монстры, предметы и прочий контент.

Любое магическое число, если сходу не понятно его назначение, должно быть заменено
именованной постоянной.
"""

__author__ = "Ecialo"

import pyglet
from pyglet.window import key
from pyglet.window import mouse
from math import sqrt


### Вспомогательное
EMPTY_LIST = []
MAX_BITMASK_SIZE = 16


def binary_list(n):
    if n >= MAX_BITMASK_SIZE:
        return []
    return map(lambda x: 2**x, range(n))


### Экран
window = {'width': 1024,
          'height': 768,
          'vsync': True,
          'resizable': True,
          'do_not_scale': True}


### Единицы измерения
TILE_SIZE_IN_PIXELS = 32


def tiles_to_pixels(tiles):
    if hasattr(tiles, '__iter__'):
        return type(tiles)([tiles_to_pixels(x) for x in tiles])
    else:
        return tiles*1.0*TILE_SIZE_IN_PIXELS


def pixels_to_tiles(pixels):
    if hasattr(pixels, '__iter__'):
        return type(pixels)([pixels_to_tiles(x) for x in pixels])
    else:
        return pixels*1.0/TILE_SIZE_IN_PIXELS


def jump_height_to_jump_speed(height_in_tiles):
    return sqrt(2*GRAVITY*height_in_tiles)


### Box2D

# Биты масок коллизий
B2SMTH, B2LEVEL, B2GNDSENS, B2HITZONE, B2ACTOR, B2SWING, B2BODYPART, B2ITEM = binary_list(8)
B2NONE = 0x0000
B2EVERY = 0xFFFF

# Постоянные мира
GRAVITY = 50

# Вращение тела
NO_ROTATION = 0


### Управление
bindings = {'left': key.A,
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
            'change_weapon': key.R}


### Параметры тел
human = {'speed': 7,
         'jump_speed': jump_height_to_jump_speed(4)}


### Параметры ИИ
primitive = {'range_of_vision': tiles_to_pixels(15),            # Тут всё в пикселях. Будет вскоре исправлено
             'mastery': 0.05,
             'closest': 40}


### HUD
body = {'back': {'head': pyglet.resource.image('ui_head_back.png'),
                 'chest': pyglet.resource.image('ui_chest_back.png'),
                 'left_arm': pyglet.resource.image('ui_left_arm_back.png'),
                 'right_arm': pyglet.resource.image('ui_right_arm_back.png'),
                 'legs': pyglet.resource.image('ui_legs_back.png')},
        'front': {'head': pyglet.resource.image('ui_head_front.png'),
                  'chest': pyglet.resource.image('ui_chest_front.png'),
                  'left_arm': pyglet.resource.image('ui_left_arm_front.png'),
                  'right_arm': pyglet.resource.image('ui_right_arm_front.png'),
                  'legs': pyglet.resource.image('ui_legs_front.png')},
        'armored': {'head': pyglet.resource.image('ui_head_armored.png'),
                    'chest': pyglet.resource.image('ui_chest_armored.png'),
                    'left_arm': pyglet.resource.image('ui_left_arm_armored.png'),
                    'right_arm': pyglet.resource.image('ui_right_arm_armored.png'),
                    'legs': pyglet.resource.image('ui_legs_armored.png')}}

status = {'health_icon': pyglet.resource.image('ui_health_icon.png')}


### Изображения
img = {'hero': pyglet.resource.image('stand.png'),
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
       'shard': pyglet.resource.image('twister_shard.png')}


### Предметы
# Слот в котором находится активный предмет
SECONDARY, MAIN = xrange(2)
# Размер предмета
SMALL, LARGE = xrange(2)


### Задачи
# Код возврата
COMPLETE = True         # ИСпользуется так же в диалогах


### Диалоги
# Состояния автомата чтения из файла
NAME, LINE = xrange(2)

# Размеры окна c текстом и отступ от портрета
DIALOG_WIDTH = 300          # По хорошему должны считаться динамически
DIALOG_HEIGHT = 128
STEP = 50

# Скорость показа текста
CHARS_PER_MINUTE = 10.0


### Инвентарь
# Размеры
MAX_INVENTORY_SIZE = 5
SEPARATE_ROW_SIZE = 1
BELT_ROW_SIZE = 1
INVENTORY_CELL_SIZE = 32        # В пикселях

# Индекс клеток пояса
BELT_CELL = -1

# Направление прокрутки пояса
NO_SCROLL = 0

consts = {'color': {'white': (255, 255, 255, 255)},
          'group': {'hero': 1,
                    'opponent': 2},
          'portrait': {'parzalon': pyglet.resource.image('parzalon_portrait.png'),
                       'enemy': pyglet.resource.image('enemy_portrait.jpg')},
          'parry_cos_disp': 0.5,
          'effective_dst': 4.0/3.0,
          'test_slash_time': 0.8,
          'rubbing': 3,
          'tile_size': 32,
          'slash_fight_group': 100,
          'missile_fight_group': 1000,
          'animation_frames': {'walk': ('2.png', '3.png')}
          }
#LEFT, UP, RIGHT, DOWN, NO_TR = 0b1000, 0b0100, 0b0010, 0b0001, 0b0000
FIRST_HAND, SECOND_HAND = xrange(2)
FIRST, SECOND = xrange(2)
HAND, HEAD, CHEST, LEGS = xrange(4)
ARMOR = 100
CHOP, STAB, CLEAVE, PENETRATE = xrange(4)
LINE, RECTANGLE = xrange(2)
UNIT, ITEM = xrange(2)
