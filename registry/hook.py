# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from .utility import module_path_to_os_path


class Global_Base(object):

    def __init__(self, registers):
        self.registers = list(registers)

    def __contains__(self, item):
        return any((item in register for register in self.registers))

    def __getitem__(self, item):
        for register in self.registers:
            if item in register:
                return register[item]
        raise KeyError

    def add_register(self, register):
        self.registers.append(register)


class Lazy_Resource_Registry(object):

    def __init__(self, resource_name):
        self.resource_name = resource_name
        self._data = None
        self.index()
        #print self._data

    def __getitem__(self, item):
        #print item
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
        #print querry
        exec querry
        #print item
        exec "tmp = %s" % item
        self[item] = tmp

    def index(self):
        import os
        resource_name = self.resource_name
        resource_path = module_path_to_os_path(resource_name)
        all_items = (item.split(".")[0] for item in os.listdir(resource_path))
        valid_items = filter(lambda x: "__" not in x, all_items)
        self._data = dict(zip(valid_items, valid_items))
        #print self._data
