# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from registry.utility import COMPLETE


class Task(object):

    environment = None

    def __init__(self, master, time=None):
        self.master = master
        self.time = time

    def __call__(self, dt):
        if self.time is not None:
            self.time -= dt
            return COMPLETE if self.time <= 0.0 else None