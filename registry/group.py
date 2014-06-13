# -*- coding: utf-8 -*-
__author__ = 'ecialo'

from .utility import binary_list

HERO, ENEMY, SWING, MISSLE = binary_list(4)

UNIT = binary_list(1)

# Основные модификаторы ударов
CHOP, STAB, PENETRATE, CLEAVE = binary_list(4)

# Геометрии
LINE, RECTANGLE = binary_list(2)