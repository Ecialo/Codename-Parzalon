# -*- coding: utf-8 -*-
from .. import bodies
Body = bodies.Body
__author__ = 'Ecialo'


class Human(Body):

    anim = {'walk': con.img['human'],
            'stand': con.img['human'],
            'jump': con.img['human'],
            'sit': con.img['human_sit']}

    parts_pos = {'walk': [(con.LEGS, (0, -77)), (con.CHEST, (0, 0)), (con.HEAD, (0, 57))],
                 'stand': [(con.LEGS, (0, -77)), (con.CHEST, (0, 0)), (con.HEAD, (0, 57))],
                 'jump': [(con.LEGS, (0, -77)), (con.CHEST, (0, 0)), (con.HEAD, (0, 57))],
                 'sit': [(con.LEGS, (0, -77)), (con.CHEST, (0, 0)), (con.HEAD, (0, 17))]}
    img = anim['stand']
    base_speed = con.human['speed']

    def __init__(self, master):
        Body.__init__(self, master, [Chest, Head, Legs], 'Human')
        self.make_animation(self.anim, 'Human')