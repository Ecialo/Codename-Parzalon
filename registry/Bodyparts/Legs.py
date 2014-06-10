__author__ = 'ecialo'

import cocos.euclid as eu
from bodypart import Body_Part
from bodypart import death
from registry.bodypart import LEGS


class Legs(Body_Part):

    slot = LEGS

    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, -77), 33, 25, 2, 2,
                           [death])
