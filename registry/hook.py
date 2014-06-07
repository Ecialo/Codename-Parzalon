# -*- coding: utf-8 -*-
"""
Здесь производится индексация ресурсов.

Ресурсы ленивые.
"""
__author__ = 'Ecialo'

from registry.utility import module_path_to_os_path


class Lazy_Resource_Registry(object):

    def __init__(self, resource_name):
        self.resource_name = resource_name
        self._data = None
        self.index()
        print self._data

    def __getitem__(self, item):
        print item
        if type(self._data[item]) is not str:
            return self._data[item]
        else:
            self.load_then_apply(item)
            return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, item):
        return item in self._data

    def load_then_apply(self, item):
        tmp = None
        querry = "from %s.%s import *" % (self.resource_name, item)
        print querry
        exec querry
        print item
        exec "tmp = %s" % item
        self[item] = tmp

    def index(self):
        import os
        resource_name = self.resource_name
        resource_path = module_path_to_os_path(resource_name)
        all_items = (item.split(".")[0] for item in os.listdir(resource_path))
        valid_items = filter(lambda x: "__" not in x, all_items)
        self._data = dict(zip(valid_items, valid_items))
        print self._data





def load_effects():
    pass


def load_usages():
    pass


def load_items():
    pass


def load_maps():
    pass


def load_tasks():
    pass


def load_brains():
    pass


def load_bodies():
    pass


def load_units():
    pass


