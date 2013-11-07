__author__ = 'Ecialo'
import consts as con
import brains
import bodies
import weapons
objs = {'hero':     {'type': con.UNIT,
                     'brain': brains.Controller,
                     'body': bodies.Hero,
                     'items': [weapons.Sword, weapons.Knife]},
        'enemy':    {'type': con.UNIT,
                     'brain': brains.Primitive_AI,
                     'body': bodies.Human,
                     'items': [weapons.Sword]},
        'dummy':    {'type': con.UNIT,
                     'brain': brains.Dummy,
                     'body': bodies.Human,
                     'items': [weapons.Sword]}}
