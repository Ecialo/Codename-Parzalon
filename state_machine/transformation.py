# -*- coding: utf-8 -*-
__author__ = 'ecialo'


class Transformation(object):

    def __init__(self, animation):
        self._animation = animation
        self._duration = animation.duration

    def apply(self, time=0.0, loop=False, skeleton=None):
        pass


class Transition(Transformation):

    def __init__(self, from_animation, to_animation):
        self._from_animation = from_animation
        self._to_animation = to_animation


class Reversed_Animation(Transformation):

    def apply(self, time=0.0, skeleton=None, loop=False):
        self._animation.apply(time=self._duration-time, skeleton=skeleton, loop=loop)