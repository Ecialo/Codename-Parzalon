__author__ = 'Ecialo'
import consts as con
import brains
import bodies
import weapons
import twister
import armors
objs = {'hero':     {'type': con.UNIT,
                     'brain': brains.Controller,
                     'body': bodies.Hero,
                     'items': [armors.Helmet, weapons.Sword] + [weapons.Knife]*10},
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
