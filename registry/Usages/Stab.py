# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from .Swing import Swing
from registry import BASE
stab = BASE['stab']


class Stab(Swing):

    def __init__(self, effects):
        effects.append(stab)
        Swing.__init__(self, effects)