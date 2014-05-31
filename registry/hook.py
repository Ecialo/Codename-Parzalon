# -*- coding: utf-8 -*-
"""
Здесь производится индексация ресурсов.

Ресурсы ленивые.
"""
__author__ = 'Ecialo'


class Lazy_Resource_Registry(object):

    def __init__(self):
        self._data = {}
        self.index()

    def __getitem__(self, item):
        if type(self._data[item]) is not str:
            return self._data[item]
        else:
            self.load_then_apply(item)
            return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def load_then_apply(self, item):
        tmp = None
        querry = "from .%s import *" % item
        exec querry
        exec "tmp = %s" % item
        self[item] = tmp

    def index(self):
        import os



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


