# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from .Swing import Swing
from registry import BASE
chop = BASE['chop']


class Chop(Swing):

    def __init__(self, effects):
        effects.append(chop)
        Swing.__init__(self, effects)