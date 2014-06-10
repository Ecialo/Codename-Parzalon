# -*- coding: utf-8 -*-
from unit import Unit

__author__ = 'Ecialo'
from registry.Bodies import bodies_base
from registry.Brains import brains_base
from registry.group import UNIT
Parzalon = Unit(UNIT, bodies_base['Human'], brains_base['Controller'], [])