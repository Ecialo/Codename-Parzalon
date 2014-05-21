# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

EMPTY_LIST = []
MAX_BITMASK_SIZE = 16
COMPLETE = True
UNCOMPLETE = False

def binary_list(n):
    if n >= MAX_BITMASK_SIZE:
        return []
    return map(lambda x: 2**x, range(n))