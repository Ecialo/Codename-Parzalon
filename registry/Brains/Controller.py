# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


class Controller(Brain):

    bind = con.bindings
    fight_group = consts['group']['hero']

    def start(self):
        Brain.start(self)
        self.task_manager.push_task(Controlling(self.master))