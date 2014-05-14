# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


class Dummy(Enemy_Brain):

    range_of_vision = con.primitive['range_of_vision']

    def start(self):
        Brain.start(self)
        self.vision = self.master.get_ancestor(layer.ScrollableLayer).collman
        self.visible_actors_wd = []
        self.visible_hits_wd = []
        self.task_manager.push_task(Task(self, 1))

        self.state = 'stand'