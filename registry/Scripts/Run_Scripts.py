# -*- coding: utf-8 -*-
__author__ = 'ecialo'

from script import Script


class Run_Scripts(Script):

    def __init__(self, map_object, environment):
        super(Run_Scripts, self).__init__(map_object, environment)

    def run(self, position):
        map_object = self.map_object
        position = map_object.position
        for scr in filter(lambda key: key.startswith('script'), map_object.properties.iterkeys()):
            self.environment.get_script_by_name(map_object[scr]).run(position)