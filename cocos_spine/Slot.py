__author__ = 'Ecialo'

from collections import namedtuple
import Box2D as b2
import Attachment

Slot_Data = namedtuple("Slot_Data", ['name', 'bone', 'color', 'attachment'])


class Slot(object):

    def __init__(self, name=None, bone=None, color=None, attachment=None):
        self.name = name
        self.bone = bone
        self.attachment = attachment
        self.color = color

        self.slot_data = None
        self.to_draw = None

    def init_b2(self):
        if self.attachment and type(self.attachment) is not unicode:
            body = self.bone.body
            width = self.attachment.width
            height = self.attachment.height
            center = self.attachment.tsr.position
            angle = self.attachment.tsr.rotation
            body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=(width, height, center, angle))))

    def apply_slot_data(self):
        self.slot_data = Slot_Data(self.name, self.bone, self.color, self.attachment)

    def set_attachment(self, image, attachment):
        self.attachment = attachment.name
        if self.to_draw:
            self.to_draw.set_new_attachment(image, attachment)
        else:
            self.to_draw = Attachment.Sprite_Attachment(image, attachment)