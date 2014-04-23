__author__ = 'Ecialo'

import json

import Bone
import Slot
import Skin

class Skeleton_Data(object):

    def __init__(self, file=None):
        self.root_bone = None
        self.bones = {}
        self.slots = {}
        self.skins = {}
        self.animations = {}
        self.defaultSkin = None
        self.load_from_json(file)

    def load_from_json(self, file):
        if file:
            with open(file) as fp:
                data = json.load(fp)
                self.load_bones(data['bones'])

        else:
            pass

    def load_bones(self, bones):
        for bone in bones:
            if self.root_bone:
                parent_name = bone['parent']
                bone['parent'] = self.bones[parent_name]
                new_bone = Bone.Bone(**bone)
                self.bones[bone['name']] = new_bone
                self.bones[parent_name].add_bone(new_bone)
            else:
                self.root_bone = Bone.Bone(**bone)
                self.bones[bone['name']] = self.root_bone

    def load_slots(self, slots):
        for slot in slots:
            slot['bone'] = self.bones[slot['bone']]
            self.slots[slot['name']] = Slot.Slot(**slot)

    def load_skins(self, skins):
        for skin in skins:
            pass


if __name__ == "__main__":
    sd = Skeleton_Data('./data/dragon.json')