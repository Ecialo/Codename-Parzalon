__author__ = 'Ecialo'


class TSR(object):

    def __init__(self, position, scale_x, scale_y, rotation):
        self.position = position
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.rotation = rotation

    def _set_x(self, x):
        self.position = (x, self.position[1])

    def _set_y(self, y):
        self.position = (self.position[0], y)