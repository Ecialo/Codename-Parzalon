# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


class Usage(object):

    owner = property(lambda self: self.master.master)

    def __call__(self, master):
        self.master = master
        return self

    def start_use(self, *args):
        pass

    def continue_use(self, *args):
        pass

    def end_use(self, *args):
        pass

    def move(self, v):
        pass

    def complete(self):
        self.master.available = True
        self.master.on_use = False