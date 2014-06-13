# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from utility import binary_list

# Биты масок коллизий
B2SMTH, B2LEVEL, B2GNDSENS, B2HITZONE, B2ACTOR, B2SWING, B2BODYPART, B2ITEM = binary_list(8)
B2NONE = 0x0000
B2EVERY = 0xFFFF

# Постоянные мира
GRAVITY = 50

# Вращение тела
NO_ROTATION = 0