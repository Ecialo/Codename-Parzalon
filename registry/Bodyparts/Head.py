__author__ = 'ecialo'
import cocos.euclid as eu
from bodypart import Body_Part
from bodypart import death
from registry.bodypart import HEAD


class Head(Body_Part):

    slot = HEAD

    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, 57), 15, 20, 2, 2,
                           [death])
