# -*- coding: utf-8 -*-
from pyglet.resource import image
from pyglet.image import Animation
from ...bodypart import *
from ..bodies import Body
from ...Bodyparts import Skull
__author__ = 'Ecialo'


class Twister(Body):

    anim = {'windwalk': Animation.from_image_sequence([img['twister']], 0.0),
            'stand': Animation.from_image_sequence([img['twister']], 0.0),
            'jump': Animation.from_image_sequence([img['twister']], 0.0)}

    parts_pos = {'walk': [(HEAD, (0, 0))],
                 'stand': [(HEAD, (0, 0))],
                 'jump': [(HEAD, (0, 0))]}
    img = image('twister.png')
    base_speed = 7

    def __init__(self, master):
        Body.__init__(self, master,
                      [Skull], 'twister_body',
                      [on_collide_damage(1)])
        self.make_animation(self.anim, 'Twister')