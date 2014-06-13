# -*- coding: utf-8 -*-
__author__ = 'ecialo'

from cocos import actions as ac
from collections import deque
from registry.utility import COMPLETE


class Task_Manager(object):

    def __init__(self):
        self.tasks = deque()

    def cur_task(self):
        if self.tasks:
            return self.tasks[0]
        else:
            return None

    def push_task(self, task):
        old_task = self.tasks.popleft() if not self.is_empty() else None
        self.tasks.appendleft(task)
        if old_task:
            self.tasks.appendleft(old_task)

    def push_instant_task(self, task):
        self.tasks.appendleft(task)

    def pop_task(self):
        return self.tasks.popleft()

    def clear_queue(self):
        self.tasks = deque()

    def num_of_tasks(self):
        return len(self.tasks)

    def is_empty(self):
        return self.num_of_tasks() <= 0


class Brain(ac.Action):

    master = property(lambda self: self.target)
    fight_group = -1

    def start(self):
        self.master.fight_group = self.fight_group
        self.environment = self.master.tilemap
        self.task_manager = Task_Manager()

    def step(self, dt):
        self.master.update(dt)
        self.sensing()
        self.activity(dt)

    def sensing(self):
        pass

    def activity(self, dt):
        if not self.task_manager.is_empty() and self.task_manager.cur_task()(dt) is COMPLETE:
            self.task_manager.pop_task()

