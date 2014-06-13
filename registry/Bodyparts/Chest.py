__author__ = 'ecialo'

import cocos.euclid as eu
from bodypart import Body_Part
from bodypart import death
from registry.bodypart import CHEST

class Chest(Body_Part):

    slot = CHEST

    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, 0), 40, 25, 2, 2,
                           [death])