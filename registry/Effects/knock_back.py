# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


def knock_back(value):
    def mast_knock_back(master):
        def fab_knock_back(body_part):
            v = master.trace.v.normalized() * value
            body_part.master.master.push(v)
        return fab_knock_back
    return mast_knock_back
