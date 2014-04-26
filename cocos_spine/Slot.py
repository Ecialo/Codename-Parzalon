__author__ = 'Ecialo'

from collections import  namedtuple

Slot_Data = namedtuple("Slot_Data", ['name', 'bone', "attachment"])


class Slot(object):

    def __init__(self, name=None, bone=None, color=None, attachment=None):
        self.name = name
        self.bone = bone
        self.attachment = attachment

        self.slot_data = None

    def apply_slot_data(self):
        self.slot_data = Slot_Data(self.name, self.bone, self.attachment)