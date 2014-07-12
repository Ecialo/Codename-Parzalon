# -*- coding: utf-8 -*-
from unit import Unit

__author__ = 'Ecialo'
from registry.group import UNIT
from registry import BASE
Human = BASE['Cool_Human']
Controller = BASE['Controller']
#Sword = BASE['Sword']
Parzalon = Unit(UNIT, Human, Controller, [])