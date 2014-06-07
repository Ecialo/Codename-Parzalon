# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from .Unit import Unit
from registry.Bodies import bodies_base
from registry.Brains import brains_base
Parzalon = Unit(0, bodies_base['Human'], brains_base['Controller'], [])