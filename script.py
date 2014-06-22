# -*- coding: utf-8 -*-
__author__ = 'ecialo'


class Script(object):

    def __init__(self, map_object, environment):
        self.environment = environment
        self.map_object = map_object
        #self.map_object.set_script(self)

    def run(self, position):
        pass

    def trigger(self):
        self.run(self.map_object.position)