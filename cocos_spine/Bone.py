__author__ = 'Ecialo'



class Bone(object):

    def __init__(self, name=None, parent=None, length=0, x=0, y=0, scaleX=0, rotation=0):
        self.name = name
        self.parent = parent
        self.length = length
        self.x = x
        self.y = y
        self.scale = scaleX
        self.rotation = rotation
        self.childs = []

    def add_bone(self, bone):
        self.childs.append(bone)
