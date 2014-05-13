from registry.Bodies import bodies
from registry.Brains import brains
from registry.Items import weapons

__author__ = 'Ecialo'
import consts as con
import twister

objs = {'hero':     {'type': con.UNIT,
                     'brain': brains.Controller,
                     'body': bodies.Hero,
                     'items': [weapons.Sword, weapons.Musket]},
        'enemy':    {'type': con.UNIT,
                     'brain': brains.Base_Enemy_Mind,
                     'body': bodies.Human,
                     'items': [weapons.Sword]},
        'dummy':    {'type': con.UNIT,
                     'brain': brains.Dummy,
                     'body': bodies.Human,
                     'items': [weapons.Sword]},
        'twister':  {'type': con.UNIT,
                     'brain': twister.Twister_Mind,
                     'body': twister.Twister_Body,
                     'items': [twister.Twister_Shard]}}
