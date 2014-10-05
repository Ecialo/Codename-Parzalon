# -*- coding: utf-8 -*-
__author__ = 'ecialo'


class Transformation(object):

    _duration = 0.0

    @property
    def duration(self):
        return self._duration

    def apply(self, time=0.0, loop=False, skeleton=None):
        pass


class Transition(Transformation):
    pass


class Instant(Transition):

    def __init__(self):
        self._duration = 0.0


class Reversed_Animation(Transformation):

    def __init__(self, animation):
        self._animation = animation
        self._duration = animation.duration

    def apply(self, time=0.0, skeleton=None, loop=False):
        self._animation.apply(time=self._duration-time, skeleton=skeleton, loop=loop)