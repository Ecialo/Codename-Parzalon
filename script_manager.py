# -*- coding: utf-8 -*-
__author__ = 'ecialo'


def passive(preprocess):

    def passive_preprocess(environment, object):
        script = preprocess(environment, object)
        return script

    return passive_preprocess


def instant(preprocess):

    def passive_preprocess(environment, object):
        script = preprocess(environment, object)
        return script

    return passive_preprocess

def entry_preprocess(environment, entry_object):
    script = None
    return script


class Script_Manger(object):

    preprocessers = {'entry': entry_preprocess}

    def __init__(self, script_layer, location):
        self.location_preprocess = location
        self.script_layer = script_layer
        self.location_preprocess()

    def location_preprocess(self):
        for object in self.script_layer:
            object.script = self.preprocessers[object.type](object)