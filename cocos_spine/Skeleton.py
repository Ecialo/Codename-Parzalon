__author__ = 'Ecialo'

import json

from cocos import batch
from cocos import sprite
from pyglet import image
import cocos
from collections import OrderedDict, namedtuple

import Bone
import Slot
import Skin
from Animation import *
import Attachment
from Atlas import *
from tsr_transform import *


def json_data_loader(filename):
    f = open(filename)
    data = json.load(f)
    f.close()
    return data

Event = namedtuple("Event", ['int', 'float', 'string'])


class Skeleton_Data(object):

    def __init__(self, file, atlas):
        self.root_bone = None
        self.bones = {}
        self.slots = OrderedDict()
        self.skins = {}
        self.animations = {}
        self.events = {}
        self.sprites = []
        #self.to_draw = OrderedDict()
        self.current_skin = None

        if type(atlas) is str:
            self.atlas = Atlas(atlas)
        elif isinstance(atlas, Atlas):
            self.atlas = atlas
        else:
            print atlas
            raise Exception("Invalid atlas")

        if type(file) is str:
            self.load_from_json(file)
        else:
            self.load_from_file(file)
        # if not self.current_skin:
        #     self.current_skin = self.skins.values()[0]
        self.sprites = [Attachment.Sprite_Attachment() for i in xrange(len(self.slots))]
        self.set_draworder(range(len(self.slots)))
        self.set_skin(self.skins.keys()[0])
        #self.prepare_to_draw()
        self.update_transform()

    def update_transform(self):
        self.root_bone.update_childs()
        for slot in self.slots.itervalues():
            bone = slot.bone
            #print bone.name, bone.rotation
            attach_to_draw = slot.to_draw
            attach_data = self.current_skin.get_attachment(slot.name, slot.attachment)
            #print slot.name, slot.attachment, attach_data
            if attach_data:
                #slot.to_draw.debug = True
                #attach_data = attach.attachment_data
                # x, y = attach.position
                # bx, by  = bone.position
                # attach.position = (x+bx, y+by)
                # attach.rotation += bone.rotation
                par_tsr = bone.global_tsr
                #print bone.global_tsr, bone.name
                new_tsr = attach_data.tsr.tsr_transform(par_tsr)
                #if slot.name == "R_wing":
                    #print attach_data.name, attach_data.tsr
                    #print slot.bone.global_tsr
                    #print new_tsr
                    #print attach_to_draw.get_rect()
                #child_tsr = (attach_data.position, attach_data.scale_x, attach_data.scale_y, attach_data.rotation)
                attach_to_draw.set_tsr_by_named_pack(new_tsr)
                #print attach.attachment_data.name, attach.rotation
                #attach.rotation *= -1

    def set_draworder(self, draworder):
        for i, slot in enumerate(self.slots.itervalues()):
            slot.set_to_draw(self.sprites[draworder[i]])
            attachment_name = slot.attachment
            if self.current_skin:
                attach = self.current_skin.get_attachment(slot.name, attachment_name)
                image = self.atlas.get_attachment_region(attach.texture_name)
                self.sprites[draworder[i]].set_new_attachment(image, attach)

    def set_skin(self, skin_name):
        if not self.current_skin or self.current_skin.name is not skin_name:
            self.current_skin = self.skins[skin_name]
            self.prepare_to_draw()
            # for slot in self.slots.itervalues():
            #     #print slot.name, slot.attachment
            #     attach = self.current_skin.get_attachment(slot.name, slot.attachment)
            #     if slot.name == "right hand item 2":
            #         print "!!!!", attach.texture_name
            #     if attach:
            #         #print self.current_skin.name, attach.name
            #         self.set_attachment(slot, attach.name)
            #     else:
            #         slot.to_draw = None

    def prepare_to_draw(self):
        # for slot_name, slot in self.slots.items():
        #     attach = self.current_skin.get_attachment(slot_name, slot.attachment)
        #     if attach:
        #         image = self.atlas.get_attachment_region(attach.texture_name)
        #         slot.set_attachment(image, attach)
        for slot in self.slots.itervalues():
            #print slot.name, slot.attachment
            attach = self.current_skin.get_attachment(slot.name, slot.attachment)
            #if slot.name == "right hand item 2":
                #print "!!!!", attach
            if attach:
                #print self.current_skin.name, attach.name
                self.set_attachment(slot, attach.name)
            else:
                slot.to_draw.set_empty_image()
                #slot.to_draw = None
            #print slot.attachment.position

    def load_from_json(self, file):
        if file:
            with open(file) as fp:
                data = json.load(fp)
                self.load_bones(data['bones'])
                if 'slots' in data:
                    self.load_slots(data['slots'])
                if 'skins' in data:
                    self.load_skins(data['skins'])
                if 'events' in data:
                    self.load_events(data['events'])
                if 'animations' in data:
                    self.load_animations(data['animations'])

        else:
            pass

    def load_from_file(self, data):
        self.load_bones(data['bones'])
        self.load_slots(data['slots'])
        self.load_skins(data['skins'])
        self.load_animations(data['animations'])

    def load_bones(self, bones):
        for bone in bones:
            if self.root_bone:
                parent_name = bone['parent']
                bone['parent'] = self.bones[parent_name]
                new_bone = Bone.Bone(**bone)
                self.bones[bone['name']] = new_bone
                self.bones[parent_name].add_bone(new_bone)
                bone['parent'] = parent_name
            else:
                self.root_bone = Bone.Bone(**bone)
                self.bones[bone['name']] = self.root_bone
            self.bones[bone['name']].apply_bone_data()

    def load_slots(self, slots):
        for slot in slots:
            slot_bone_name = slot['bone']
            slot['bone'] = self.bones[slot_bone_name]
            self.slots[slot['name']] = Slot.Slot(**slot)
            self.slots[slot['name']].apply_slot_data()
            slot['bone'] = slot_bone_name

    def load_skins(self, skins):
        for skin_name, skin in skins.items():
            new_skin = Skin.Skin(skin_name)
            self.skins[skin_name] = new_skin
            #if skin_name == 'default':
            #    self.current_skin = new_skin
            for slot_name, attachments in skin.items():
                for attach_name, attach in attachments.items():
                    #attach['image'] = self.atlas.get_attachment_region(attach_name)
                    if 'type' not in attach:
                        attach_type = 'region'
                    else:
                        attach_type = attach['type']
                    if attach_type == 'region':
                        if 'name' not in attach:
                            attach['name'] = attach_name
                            attach['texture_name'] = attach_name
                            attach_data = Attachment.Attachment(**attach)
                            new_skin.add_attachment(slot_name, attach_name, attach_data)
                        else:
                            data_attach_name = attach['name']
                            attach['texture_name'] = data_attach_name
                            attach['name'] = attach_name
                            attach_data = Attachment.Attachment(**attach)
                            new_skin.add_attachment(slot_name, attach_name, attach_data)
                            attach['name'] = data_attach_name
                    elif attach_type == 'regionsequence':
                        print "Warning: unsupported attachment type regionsequence"
                    elif attach_type == 'boundingbox':
                        print "Warning: unsupported attachment type boundingbox"
                    else:
                        print "Error: unknown attachment type"

    def load_events(self, events):
        for event_name, event in events:
            event_int = event['int'] if 'int' in event else 0
            event_float = event['float'] if 'float' in event else 0
            event_string = event['string'] if 'string' in event else ""
            self.events[event_name] = Event(event_int, event_float, event_string)

    def load_animations(self, animations):
        for animation in animations:
            loaded_animation = Animation(animation, animations[animation])
            self.animations[animation] = loaded_animation
            loaded_animation.apply_bones_and_slots_data(self)

    def set_attachment(self, slot, attachment_name):
        #print attachment_name
        #print self.current_skin.attachments
        attach = self.current_skin.get_attachment(slot.name, attachment_name)
        #print attachment_name
        image = self.atlas.get_attachment_region(attach.texture_name)
        slot.attachment = attach.name
        #if slot.to_draw:
        slot.to_draw.set_new_attachment(image, attach)
        # else:
        #     #print "LOLOLO", attach.name
        #     slot.to_draw = Attachment.Sprite_Attachment(image, attach)

    def find_animation(self, animation_name):
        return self.animations[animation_name]


class Skeleton(batch.BatchableNode):

    def __init__(self, skeleton_data, b2world):
        super(Skeleton, self).__init__()
        self.skeleton_data = skeleton_data
        self.b2world = b2world
        self.skeleton_data.root_bone.init_b2(self.b2world)
        for i, sp in enumerate(self.skeleton_data.sprites):
            self.add(sp, z=i)
        self.render()
        for slot in self.skeleton_data.slots.itervalues():
            slot.init_b2()

    def debag(self):
        for lol in self.skeleton_data.slots.itervalues():
            if lol.debag_box:
                self.add(lol.debag_box, z=100)

    def set_skin(self, skin_name):
        self.skeleton_data.set_skin(skin_name)
        self.render()

    def find_animation(self, animation_name):
        return self.skeleton_data.find_animation(animation_name)

    def render(self):
        for slot in self.skeleton_data.slots.itervalues():
            attach = slot.to_draw
        #i = 0
        #print self.skeleton_data.to_draw.keys()
        # for slot in self.skeleton_data.slots.itervalues():
        #     attach = slot.to_draw
        #     slot_name = slot.name
        #     try:
        #         already = self.get(slot_name)
        #         #print already
        #         if not attach:
        #             already.kill()
        #     except:
        #         if attach:
        #             self.add(attach, z=i, name=slot_name)
        #     finally:
        #         i += 1

    # def visit(self):
    #     #self.skeleton_data.update_transform()
    #     super(Skeleton, self).visit()

    def _set_position(self, p):
        self.skeleton_data.root_bone.local_tsr.position = p

    def _set_rotation(self, a):
        self.skeleton_data.root_bone.local_tsr.rotation = a

    def _set_scale(self, s):
        self.skeleton_data.root_bone.local_tsr.scale_x = s
        self.skeleton_data.root_bone.local_tsr.scale_y = s

    def _set_scale_x(self, s):
        self.skeleton_data.root_bone.local_tsr.scale_x = s

    def _set_scale_y(self, s):
        self.skeleton_data.root_bone.local_tsr.scale_y = s


def main():

    from cocos.draw import Canvas, parameter
    from cocos import layer
    from cocos import scene
    from cocos.director import director
    import Box2D as b2
    #import json
    director.init(1024, 768, do_not_scale=True)

    class Box(Canvas):
        r = parameter()
        stroke_width = parameter()
        color = parameter()

        def __init__(self, position, size, color, b2world, stroke_width=1):
            super(Box, self).__init__()
            #self.r = rectangular
            self.hw, self.hh = size
            self.color = color
            self.stroke_width = stroke_width
            self.body = b2world.CreateDynamicBody()
            self.body.position = position
            self.body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=(self.hw, self.hh))))
            self.schedule(self.update)

        def update(self, dt):
            self.position = self.body.position

        def render(self):
            #print 1
            plb = (-self.hw, -self.hh)
            plt = (-self.hw, self.hh)
            prb = (self.hw, -self.hh)
            prt = (self.hw, self.hh)
            self.set_color(self.color)
            self.set_stroke_width(self.stroke_width)

            self.move_to(plb)
            self.line_to(plt)

            self.move_to(plt)
            self.line_to(prt)

            self.move_to(prt)
            self.line_to(prb)

            self.move_to(prb)
            self.line_to(plb)

    class TestLayer(layer.Layer):

        test_animation = True

        def __init__(self):
            super(TestLayer, self).__init__()
            self.b2world = b2.b2World(gravity=(0, -20))
            self.time = 0.0
            #self.name = 'spineboy'
            #self.name = 'goblins'
            #self.name = 'dragon'
            self.name = 'skeleton'
            name = self.name
            if name == 'dragon':
                sd = Skeleton_Data('./data/'+name+'.json', './data/'+name+'.atlas')

                #sd = Skeleton_Data('./data/dragon.json', './data/dragon.atlas')
                #sd = Skeleton_Data('./data/skeleton.json', './data/skeleton.atlas')
                skel = Skeleton(sd)
                self.skel = skel
                self.animation = skel.find_animation('flying')
                skel.position = (512, 200)
                self.skel.skeleton_data.update_transform()
                #self.skel.set_skin('goblingirl')
                #self.skel.set_skin('goblin')
                self.add(skel)
                self.schedule(self.update)
            elif name == 'skeleton':
                sd = Skeleton_Data('./cocos_spine/'+name+'.json', './cocos_spine/'+name+'.atlas')
                skel = Skeleton(sd, self.b2world)
                self.skel = skel
                self.skel.debag()
                self.animation = skel.find_animation('jump')
                skel.position = (512, 200)
                self.skel.skeleton_data.update_transform()
                #self.skel.set_skin('goblingirl')
                #self.skel.set_skin('goblin')
                self.add(skel)
                self.schedule(self.update)
                self.skel.add(Box((-35, 200), (20, 20), (255, 255, 255, 255),self.b2world))
            elif name == 'spineboy':
                sd = Skeleton_Data('./cocos_spine/data/'+name+'.json', './cocos_spine/data/'+name+'.atlas')
                skel = Skeleton(sd, self.b2world)
                self.skel = skel
                self.skel.debag()
                self.anim1 = skel.find_animation('walk')
                self.anim2 = skel.find_animation('jump')
                skel.position = (512, 200)
                self.add(skel)
                self.schedule(self.update)
            else:
                jd = json_data_loader('./data/'+name+'.json')
                print jd
                at = Atlas('./data/'+name+'.atlas')
                sd = Skeleton_Data(jd, at)
                sd2 = Skeleton_Data(jd, at)

                #sd = Skeleton_Data('./data/dragon.json', './data/dragon.atlas')
                #sd = Skeleton_Data('./data/skeleton.json', './data/skeleton.atlas')
                skel = Skeleton(sd)
                self.skel = skel
                self.anim1 = self.skel.find_animation('walk')
                skel2 = Skeleton(sd2)
                self.skel2 = skel2
                self.anim2 = self.skel2.find_animation('walk')
                self.batch = batch.BatchNode()
                self.batch.position = (220, 200)
                #self.animation = skel.find_animation('flying')
                skel.position = (312, 200)
                skel.scale = 2
                skel2.position = (612, 200)
                self.skel.set_skin('goblingirl')
                self.skel2.set_skin('goblingirl')
                self.skel.set_skin('goblin')
                #print skel.get('right hand item 2')
                self.skel.skeleton_data.update_transform()
                self.skel2.skeleton_data.update_transform()
                self.batch.add(skel)
                self.batch.add(skel2)
                skel2.position = (500, 220)
                self.add(self.batch)
                self.schedule(self.update)

        def update(self, dt):
            if self.name == 'dragon':
                self.time += dt/5
                self.animation.apply(skeleton=self.skel,
                                     time=self.time,
                                     loop=True)
                self.skel.skeleton_data.update_transform()
            elif self.name == 'spineboy':
                self.time += dt/20
                self.anim2.apply(skeleton=self.skel,
                                     time=self.time,
                                     loop=True)
                self.anim1.mix(skeleton=self.skel,
                               time=self.time,
                               loop=True,
                               alpha=0.5)
                self.skel.skeleton_data.update_transform()
            elif self.name == 'skeleton':
                self.time += dt/5
                self.animation.apply(skeleton=self.skel,
                                     time=self.time,
                                     loop=True)
                self.skel.skeleton_data.update_transform()
                self.b2world.Step(dt/5,1,1)
            else:
                self.time += dt
                self.anim1.apply(skeleton=self.skel,
                                 time=self.time,
                                 loop=True)
                self.anim2.apply(skeleton=self.skel2,
                                 time=self.time,
                                 loop=True)
                self.skel.skeleton_data.update_transform()
                self.skel2.skeleton_data.update_transform()






    scene = scene.Scene(TestLayer())
    director.run(scene)


    #sd = Skeleton_Data('./data/dragon.json', './data/dragon.atlas')

if __name__ == "__main__":
    main()