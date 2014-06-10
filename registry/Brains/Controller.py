# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from brain import Brain
from registry.controls import bindings
from registry.Tasks import tasks_base
from registry.group import HERO
Controlling = tasks_base['Control']


class Controller(Brain):

    bind = bindings
    fight_group = HERO

    def start(self):
        Brain.start(self)
        self.task_manager.push_task(Controlling(self.master))