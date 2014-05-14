# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Stand(Task):

    def __call__(self, dt):
        self.master.stand()
        return COMPLETE