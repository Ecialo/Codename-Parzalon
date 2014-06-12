# -*- coding: utf-8 -*-
__author__ = "Ecialo"

import pyglet
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