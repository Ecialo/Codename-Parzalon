# -*- coding: utf-8 -*-
__author__ = 'ecialo'


def passive(preprocess):

    def passive_preprocess(environment, object):
        script = preprocess(environment, object)
        return script

    return passive_preprocess


def instant(preprocess):

    def passive_preprocess(environment, object):
        preprocess(environment, object)
        return None

    return passive_preprocess


def entry_preprocess(environment, entry_object):
    script = None
    return script


class Script_Manger(object):

    preprocessers = {'entry': entry_preprocess}
    modes = {'passive': passive}

    def __init__(self, script_layer, location):
        self.location_preprocess = location
        self.script_layer = script_layer
        self.location_preprocess()

    def location_preprocess(self):
        preprocess = self.preprocessers
        modes = self.modes
        to_delete = []
        for object in self.script_layer:
            mode = object['mode']
            result = modes[mode](preprocess[object.type])(object)
            if result:
                object.script = result
            else:
                to_delete.append(object)

        for item in to_delete:
            del self.script_layer[item.name]