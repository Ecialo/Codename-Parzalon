# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Helmet(Armor):

    slot = con.HEAD

    def __init__(self):
        Armor.__init__(self, consts['img']['helmet'], Helmet_Shell())