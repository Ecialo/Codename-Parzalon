__author__ = 'Pavgran'

from cocos import sprite
from collections import namedtuple
from TSR import *

Attachment_Data = namedtuple("Attachment_Data", ['name', 'position', 'scale_x', 'scale_y',
                                                 'rotation', 'width', 'height'])


class Attachment(object):

    def __init__(self, attachment_name=None, name=None, x=0, y=0, scaleX=1, scaleY=1, rotation=0, width=0, height=0):
        self.name = name
        self.attachment_name = attachment_name
        self.tsr = TSR((x, y), scaleX, scaleY, rotation)
        self.width = width
        self.height = height


class Sprite_Attachment(sprite.Sprite):

    def __init__(self, image, attachment):
        self.name = attachment.attachment_name
        #print attachment.name
        #self.attachment_data = attachment
        position = attachment.tsr.position
        rotation = attachment.tsr.rotation
        #image = image           # We must place here image from atlas
        super(Sprite_Attachment, self).__init__(image, position)
        self.rotation = rotation
        self.scale_x = attachment.tsr.scale_x
        self.scale_y = attachment.tsr.scale_y

    def _set_rotation(self, a):
        a *= -1
        super(Sprite_Attachment, self)._set_rotation(a)

    def set_new_attachment(self, image, attachment):
        self.name = attachment.attachment_name
        #self.attachment_data = attachment
        self.image = image
        self.position = attachment.tsr.position
        self.scale_x = attachment.tsr.scale_x
        self.scale_y = attachment.tsr.scale_y
        self.rotation = attachment.tsr.rotation

    def set_tsr_by_named_pack(self, pack):
        self.position = pack.position
        self.scale_x = pack.scale_x
        self.scale_y = pack.scale_y
        self.rotation = pack.rotation
