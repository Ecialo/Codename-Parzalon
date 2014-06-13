# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from .hook import Global_Base
from .Attributes import attributes_base
from .Bodies import bodies_base
from .Bodyparts import bodyparts_base
from .Brains import brains_base
from .Effects import effects_base
from .Items import items_base
from .Levels import levels_base
from .Tasks import tasks_base
from .Units import units_base
from .Usages import usages_base

BASE = Global_Base([attributes_base, bodies_base, bodyparts_base, brains_base, effects_base,
                    items_base, levels_base, tasks_base, units_base, usages_base])