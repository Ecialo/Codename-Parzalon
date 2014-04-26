__author__ = 'Ecialo'

from collections import namedtuple

Bone_Data = namedtuple("Bone_Data", ['name', 'parent', 'length', 'position', 'scale', 'rotation', 'childs'])


class Bone(object):

    def __init__(self, name=None, parent=None, length=0, x=0, y=0, scaleX=0, rotation=0):

        self.bone_data = None

        self.name = name
        self.parent = parent
        self.length = length
        self.position = (x, y)
        self.scale = scaleX
        self.rotation = rotation
        self.childs = []

    def update_childs(self):
        data = (self.position, self.scale, self.rotation)
        reduce(lambda _, child: child.update(data), self.childs, None)

    def update(self, data):
        self.position, self.scale, self.rotation = data
        self.update_childs()

    def add_bone(self, bone):
        self.childs.append(bone)

    def apply_bone_data(self):
        self.bone_data = Bone_Data(self.name, self.parent, self.length, self.position, self.scale,
                                   self.rotation, self.childs)
