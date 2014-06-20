__author__ = 'Ecialo'

from collections import namedtuple
import Box2D as b2
import Attachment
from cocos.draw import Canvas, parameter

Slot_Data = namedtuple("Slot_Data", ['name', 'bone', 'color', 'attachment'])


class Box(Canvas):
        r = parameter()
        stroke_width = parameter()
        color = parameter()

        def __init__(self, size, color, body, stroke_width=1):
            super(Box, self).__init__()
            #self.r = rectangular
            self.hw, self.hh = size
            self.color = color
            self.stroke_width = stroke_width
            self.body = body
            self.schedule(self.update)

        def update(self, dt):
            self.position = self.body.position
            self.rotation = self.body.angle

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


class Slot(object):

    def __init__(self, name=None, bone=None, color=None, attachment=None):
        self.name = name
        self.bone = bone
        self.attachment = attachment
        self.color = color

        self.debag_box = None

        self.slot_data = None
        self.to_draw = None

    def init_b2(self):
        if self.to_draw:
            attach = self.to_draw
            body = self.bone.body
            width = attach.width
            height = attach.height
            center = attach.position
            angle = attach.rotation
            body.CreateFixture(b2.b2FixtureDef(shape=b2.b2PolygonShape(box=(width, height, center, angle))))
            self.debag_box = Box((width, height), body, (255,255,255,255))

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
