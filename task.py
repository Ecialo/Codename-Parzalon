# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Task(object):

    #hands = property(lambda self: self.master.hands)
    environment = None

    def __init__(self, master, time=None):
        self.master = master
        self.time = time

    def __call__(self, dt):
        if self.time is not None:
            self.time -= dt
            return COMPLETE if self.time <= 0.0 else None