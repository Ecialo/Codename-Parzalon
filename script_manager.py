# -*- coding: utf-8 -*-
__author__ = 'ecialo'
from registry.Scripts import scripts_base


from registry.utility import to_data_name


def passive(script):

    def passive_preprocess(map_object, environment):
        passive_script = script(map_object, environment)
        map_object.set_script(passive_script)
        return True

    return passive_preprocess


def instant(script):

    def instant_preprocess(map_object, environment):
        instant_script = script(map_object, environment)
        #print instant_script
        instant_script.run(map_object.position)
        return False

    return instant_preprocess


class Script_Manager(object):

    modes = {'passive': passive,
             'instant': instant}

    def __init__(self, script_layer, location):
        self.location = location
        self.script_layer = script_layer
        self.location_preprocess()

    def location_preprocess(self):
        modes = self.modes
        location = self.location
        to_delete = []
        for map_object in self.script_layer:
            print map_object
            mode = map_object['mode']
            result = modes[mode](scripts_base[to_data_name(map_object.type)])(map_object, location)
            if not result:
                to_delete.append(map_object)

        for item in to_delete:
            del self.script_layer[item.name]

    def get_script_by_name(self, name):
        return self.script_layer[name]