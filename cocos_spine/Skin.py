__author__ = 'Ecialo'

from collections import OrderedDict

class Skin(object):

    def __init__(self, name):
        self.name = name
        self.attachments = OrderedDict()

    def add_attachment(self, slot_name, attach_name, attach_data):
        self.attachments[(slot_name, attach_name)] = attach_data

    def get_attachment(self, slot_name, attach_name):
        return self.attachments.get((slot_name, attach_name), None)
