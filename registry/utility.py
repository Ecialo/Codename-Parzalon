# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

EMPTY_LIST = []
MAX_BITMASK_SIZE = 16
COMPLETE = True
UNCOMPLETE = False


def interval_proection(point, interval):
    """
    Return point in interval closet to given
    """
    if interval[0] <= point < interval[1]:
        return point
    elif point < interval[0]:
        return interval[0]
    else:
        return interval[1]


def module_path_to_os_path(path):
    return "./" + path.replace(".", "/") + "/"


def include(index):
    return index + 1


def binary_list(n):
    if n == 1:
        return 1
    if n >= MAX_BITMASK_SIZE:
        return []
    return map(lambda x: 2**x, xrange(n))


def Animate(master, name):
    if master.state != name:
        master.state = name
        master.image = master.body.anim[name]