__author__ = 'Ecialo'

from collections import namedtuple
from tsr_transform import *

Bone_Data = namedtuple("Bone_Data", ['name', 'parent', 'length', 'position', 'scale_x', 'scale_y', 'rotation', 'childs'])


class Bone(object):

    def __init__(self, name=None, parent=None, length=0, x=0, y=0, scaleX=1, scaleY=1, rotation=0):

        self.bone_data = None

        self.name = name
        self.parent = parent
        self.length = length
        self.position = (x, y)
        self.scale_x = scaleX
        self.scale_y = scaleY
        self.rotation = rotation
        self.childs = []

    def update_childs(self):
        data = (self.position, self.scale_x, self.scale_y, self.rotation)
        reduce(lambda _, child: child.update(data), self.childs, None)

    def update(self, data):
        #self.position, self.scale, self.rotation = data
        #pos, scale_x, scale_y, rot = self.bone_data[3:7:]
        #par_pos, par_scale_x, par_scale_y, par_rot = data
        self.position, self.scale_x, self.scale_y, self.rotation = tsr_transform(data, self.bone_data[3:7:])
        self.update_childs()

    def add_bone(self, bone):
        self.childs.append(bone)

    def apply_bone_data(self):
        self.bone_data = Bone_Data(self.name, self.parent, self.length, self.position,
                                   self.scale_x, self.scale_y, self.rotation, self.childs)
