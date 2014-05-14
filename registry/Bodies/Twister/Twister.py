# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


class Twister(bodies.Body):

    anim = {'windwalk': Animation.from_image_sequence([con.img['twister']], 0.0),
            'stand': Animation.from_image_sequence([con.img['twister']], 0.0),
            'jump': Animation.from_image_sequence([con.img['twister']], 0.0)}

    parts_pos = {'walk': [(con.HEAD, (0, 0))],
                 'stand': [(con.HEAD, (0, 0))],
                 'jump': [(con.HEAD, (0, 0))]}
    img = con.img['twister']
    base_speed = con.human['speed']

    def __init__(self, master):
        bodies.Body.__init__(self, master,
                             [Skull], 'twister_body',
                             [on_collide_damage(1)])
        self.make_animation(self.anim, 'Twister')