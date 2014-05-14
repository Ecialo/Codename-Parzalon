# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Chop(Swing):

    def __init__(self, effects):
        effects.append(on_h.chop)
        Swing.__init__(self, effects)