# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from task import Task
from registry.utility import COMPLETE

class Stand(Task):

    def __call__(self, dt):
        self.master.stand()
        return COMPLETE