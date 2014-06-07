# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

EMPTY_LIST = []
MAX_BITMASK_SIZE = 16
COMPLETE = True
UNCOMPLETE = False


def module_path_to_os_path(path):
    return "./" + path.replace(".", "/") + "/"


def include(index):
    return index + 1


def binary_list(n):
    if n >= MAX_BITMASK_SIZE:
        return []
    return map(lambda x: 2**x, range(n))


def Animate(master, name):
    if master.state != name:
        master.state = name
        master.image = master.body.anim[name]