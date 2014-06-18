__author__ = 'Ecialo'

from collections import namedtuple
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

    def apply_slot_data(self):
        self.slot_data = Slot_Data(self.name, self.bone, self.color, self.attachment)

    def set_to_draw(self, sprite_attachment):
        self.to_draw = sprite_attachment

    def set_attachment(self, image, attachment):
        self.attachment = attachment.name
        self.to_draw.set_new_attachment(image, attachment)
        # if self.to_draw:
        #     self.to_draw.set_new_attachment(image, attachment)
        # else:
        #     self.to_draw = Attachment.Sprite_Attachment(image, attachment)