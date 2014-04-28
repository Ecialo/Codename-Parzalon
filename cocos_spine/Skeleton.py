__author__ = 'Ecialo'

import json

from cocos import batch
import cocos
from collections import OrderedDict

import Bone
import Slot
import Skin
from Animation import *
import Attachment
from Atlas import *
from tsr_transform import *


class Skeleton_Data(object):

    def __init__(self, file, atlas):
        if type(atlas) is str:
            self.atlas = Atlas(atlas)
        elif isinstance(atlas, Atlas):
            self.atlas = atlas
        else:
            raise Exception("Invalid atlas")
        self.root_bone = None
        self.bones = {}
        self.slots = OrderedDict()
        self.skins = {}
        self.animations = {}
        self.to_draw = OrderedDict()
        self.current_skin = None
        self.load_from_json(file)
        if self.current_skin:
            self.prepare_to_draw()
            self.update_transform()

    def update_transform(self):
        self.root_bone.update_childs()
        for slot in self.slots.itervalues():
            if slot.name in self.to_draw:
                bone = slot.bone
                attach = self.to_draw[slot.name]
                attach_data = attach.attachment_data
                # x, y = attach.position
                # bx, by  = bone.position
                # attach.position = (x+bx, y+by)
                # attach.rotation += bone.rotation
                par_tsr = (bone.position, bone.scale_x, bone.scale_y, bone.rotation)
                child_tsr = (attach_data.position, attach_data.scale_x, attach_data.scale_y, attach.rotation)
                attach.position, attach.scale_x, attach.scale_y, attach.rotation = tsr_transform(par_tsr, child_tsr)
                attach.rotation *= -1

    def set_skin(self, skin_name):
        if not self.current_skin or self.current_skin.name is not skin_name:
            self.current_skin = self.skins[skin_name]
            self.prepare_to_draw()
            self.update_transform()

    def set_attachment_to_slot(self, slot, attachment):
        slot.attachment.image = self.atlas.get_attachment_region(attachment)

    def prepare_to_draw(self):
        for slot_name, slot in self.slots.items():
            attach = self.current_skin.get_attachment(slot_name, slot.attachment)
            if attach:
                image = self.atlas.get_attachment_region(attach.name)
                if slot.name in self.to_draw:
                    self.to_draw[slot.name].set_new_attachment(image, attach)
                else:
                    self.to_draw[slot.name] = Attachment.Sprite_Attachment(image, attach)
            #print slot.attachment.position

    def load_from_json(self, file):
        if file:
            with open(file) as fp:
                data = json.load(fp)
                self.load_bones(data['bones'])
                self.load_slots(data['slots'])
                self.load_skins(data['skins'])
                #self.load_animations(data['animations'])

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
            self.bones[bone['name']].apply_bone_data()

    def load_slots(self, slots):
        for slot in slots:
            slot['bone'] = self.bones[slot['bone']]
            self.slots[slot['name']] = Slot.Slot(**slot)
            self.slots[slot['name']].apply_slot_data()

    def load_skins(self, skins):
        for skin_name, skin in skins.items():
            new_skin = Skin.Skin(skin_name)
            self.skins[skin_name] = new_skin
            if skin_name == 'default':
                self.current_skin = new_skin
            for slot_name, attachments in skin.items():
                for attach_name, attach in attachments.items():
                    print attach
                    #attach['image'] = self.atlas.get_attachment_region(attach_name)
                    if 'name' not in attach:
                        attach_data = Attachment.Attachment(name=attach_name, **attach)
                    else:
                        attach_data = Attachment.Attachment(**attach)
                    new_skin.add_attachment(slot_name, attach_name, attach_data)

    def load_animations(self, animations):
        for animation in animations:
            loaded_animation = Animation(animation, animations[animation])
            self.animations[animation] = loaded_animation
            loaded_animation.apply_bones_and_slots_data(self)


class Skeleton(batch.BatchableNode):

    def __init__(self, skeleton_data):
        super(Skeleton, self).__init__()
        self.skeleton_data = skeleton_data
        self.render()

    def set_skin(self, skin_name):
        self.skeleton_data.set_skin(skin_name)
        self.render()

    def render(self):
        i = 0
        #print self.skeleton_data.to_draw.keys()
        for slot in self.skeleton_data.slots.keys():
            if slot in self.skeleton_data.to_draw:
                attach = self.skeleton_data.to_draw[slot]
                print attach
                self.add(attach, z=i, name=attach.name)
                i += 1


def main():

    from cocos import layer
    from cocos import scene
    from cocos.director import director
    director.init(1024, 768)

    class TestLayer(layer.Layer):
        def __init__(self):
            super(TestLayer, self).__init__()
            #name = 'goblins'
            name = 'dragon'
            #TODO Check how scale work with skins
            sd = Skeleton_Data('./data/'+name+'.json', './data/'+name+'.atlas')
            #sd = Skeleton_Data('./data/dragon.json', './data/dragon.atlas')
            #sd = Skeleton_Data('./data/skeleton.json', './data/skeleton.atlas')
            skel = Skeleton(sd)
            #skel.set_skin('goblin')
            #skel.set_skin('goblingirl')
            skel.position = (512, 200)
            self.add(skel)





    scene = scene.Scene(TestLayer())
    director.run(scene)


    #sd = Skeleton_Data('./data/dragon.json', './data/dragon.atlas')

if __name__ == "__main__":
    main()