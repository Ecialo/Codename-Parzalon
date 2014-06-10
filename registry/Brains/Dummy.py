# -*- coding: utf-8 -*-
from brain import Brain
from registry.group import ENEMY
__author__ = 'Ecialo'


class Dummy(Brain):

    fight_group = ENEMY
    range_of_vision = 15