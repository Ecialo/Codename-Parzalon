__author__ = 'Ecialo'

from collections import namedtuple
import math
import Box2D as b2
from tsr_transform import *
from TSR import *

Bone_Data = namedtuple("Bone_Data", ['name', 'parent', 'length', 'tsr'])


class Bone(object):

    def __init__(self, name=None, parent=None, length=0, x=0, y=0, scaleX=1, scaleY=1, rotation=0):

        self.bone_data = None

        self.name = name
        self.local_tsr = TSR((x, y), scaleX, scaleY, rotation)
        self.global_tsr = TSR()
        self.parent = parent
        self.length = length
        self.childs = []
        self.body = None

    def init_b2(self, b2world):
        self.body = b2world.CreateDynamicBody(gravityScale=0, allowSleep=False, userData=self)
        self.body.position = self.global_tsr.position
        self.body.angle = math.radians(self.global_tsr.rotation)
        if self.parent:
            #b2world.CreateJoint(type=b2.b2RevoluteJointDef, bodyA=self.parent.body, bodyB=self.body)
            pass
        for child in self.childs:
            child.init_b2(b2world)

    def update_childs(self):
        data = self.global_tsr
        reduce(lambda _, child: child.update(data), self.childs, None)

    def update(self, data):
        #self.position, self.scale, self.rotation = data
        #pos, scale_x, scale_y, rot = self.bone_data[3:7:]
        #par_pos, par_scale_x, par_scale_y, par_rot = data
        #self.position, self.scale_x, self.scale_y, self.rotation = tsr_transform(data, self.bone_data[3:7:])
        transformed_data = self.local_tsr.tsr_transform(data)
        self.global_tsr.set_by_named_pack(transformed_data)
        if self.body:
            self.body.position = self.global_tsr.position
            self.body.angle = math.radians(self.global_tsr.rotation)
        self.update_childs()

    def add_bone(self, bone):
        self.childs.append(bone)

    def apply_bone_data(self):
        self.bone_data = Bone_Data(self.name, self.parent, self.length, self.local_tsr.copy())
