__author__ = 'Ecialo'

from collections import namedtuple
import Attachment

Slot_Data = namedtuple("Slot_Data", ['name', 'bone', "attachment"])


class Slot(object):

    def __init__(self, name=None, bone=None, color=None, attachment=None):
        self.name = name
        self.bone = bone
        self.attachment = attachment

        self.slot_data = None
        self.to_draw = None

    def apply_slot_data(self):
        self.slot_data = Slot_Data(self.name, self.bone, self.attachment)

    def set_attachment(self, image, attachment):
        self.attachment = attachment
        if self.to_draw:
            self.to_draw.set_new_attachment(image, attachment)
        else:
            self.to_draw = Attachment.Sprite_Attachment(image, attachment)