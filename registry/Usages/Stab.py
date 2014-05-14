# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Stab(Swing):

    def __init__(self, effects):
        effects.append(on_h.stab)
        Swing.__init__(self, effects)