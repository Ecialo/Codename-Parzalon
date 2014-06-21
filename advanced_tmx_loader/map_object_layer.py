# -*- coding: utf-8 -*-
__author__ = 'ecialo'
from itertools import chain


class Map_Object_Layer(object):

    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
        self.types = {}
        self.names = {}

    def get_by_name(self, name):
        return self.names.get(name)

    def get_all_of_type(self, type_name):
        return self.types.get(type_name)

    def add(self, map_object):
        type_name = map_object.type
        name = map_object.name
        self.names[name] = map_object
        try:
            self.types[type_name].append(map_object)
        except KeyError:
            self.types[type_name] = [map_object]

    def __getitem__(self, item):
        self.get_by_name(item)

    def __delitem__(self, key):
        item = self.names[key]
        self.types[item.type].remove(item)
        self.names[key] = None

    def __iter__(self):
        for item in chain(*self.types.itervalues()):
            yield item