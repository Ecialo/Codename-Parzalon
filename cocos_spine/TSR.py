__author__ = 'Ecialo'

from tsr_transform import *


class TSR(object):

    __slots__ = ['position', 'scale_x', 'scale_y', 'rotation']

    def __init__(self, position=(0, 0), scale_x=1, scale_y=1, rotation=0):
        self.position = position
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.rotation = rotation# % 360

    #def _set_rotation(self, rotation):
    #    self._rotation = rotation % 360

    #def _get_rotation(self):
    #    return self._rotation

    #rotation = property(_get_rotation, _set_rotation)

    def set_by_named_pack(self, pack):
        self.position = pack.position
        self.scale_x = pack.scale_x
        self.scale_y = pack.scale_y
        self.rotation = pack.rotation

    def __str__(self):
        return "position: " + str(self.position) + \
               " scale_x: " + str(self.scale_x) + \
               " scale_y: " + str(self.scale_y) + \
               " rotation: " + str(self.rotation)

    def _set_x(self, x):
        self.position = (x, self.position[1])

    def _set_y(self, y):
        self.position = (self.position[0], y)

    def _get_x(self):
        return self.position[0]

    def _get_y(self):
        return self.position[1]

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def copy(self):
        return TSR(self.position, self.scale_x, self.scale_y, self.rotation)

    def tsr_transform(self, parent):
        par_pack = (parent.position, parent.scale_x, parent.scale_y, parent.rotation)
        self_pack = (self.position, self.scale_x, self.scale_y, self.rotation)
        return TSR(*tsr_transform(par_pack, self_pack))

    def reflect(self, point):
        ntsr = self.copy()
        x, y = self.position
        cx, cy = point
        ntsr.position = (-(x - cx) + cx, y)
        ntsr.rotation = 180 - self.rotation
        #ntsr.scale_x *= -1
        ntsr.scale_y *= -1
        return ntsr
