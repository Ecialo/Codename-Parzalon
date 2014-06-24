__author__ = 'Pavgran'

from cocos import sprite
from pyglet import image
from collections import namedtuple
from TSR import *
from cocos.draw import *

Attachment_Data = namedtuple("Attachment_Data", ['name', 'position', 'scale_x', 'scale_y',
                                                 'rotation', 'width', 'height'])


class Box(Canvas):
    r = parameter()
    stroke_width = parameter()
    color = parameter()

    def __init__(self, rect, color, stroke_width=1):
        super(Box, self).__init__()
        self.r = rect
        self.hw, self.hh = rect.width/2, rect.height/2
        self.color = color
        self.stroke_width = stroke_width
        #self.schedule(self.update)

    def update(self, dt):
        self.position = self.r.center

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

    def set_batch(self, *args):
        pass


class Attachment(object):

    def __init__(self, texture_name=None, name=None, x=0, y=0, scaleX=1, scaleY=1, rotation=0, width=0, height=0):
        self.name = name
        self.texture_name = texture_name
        self.tsr = TSR((x, y), scaleX, scaleY, rotation)
        self.width = width
        self.height = height


class Sprite_Attachment(sprite.Sprite):

    def __init__(self, image=image.SolidColorImagePattern((0, 0, 0, 0)).create_image(2, 2),
                 attachment=Attachment(), debug=False):
        if attachment:
            self.name = attachment.name
            #print attachment.name
            self.attachment_data = attachment
            position = attachment.tsr.position
            rotation = attachment.tsr.rotation
            #image = image           # We must place here image from atlas
            super(Sprite_Attachment, self).__init__(image, position)
            self.rotation = rotation
            self.scale_x = attachment.tsr.scale_x
            self.scale_y = attachment.tsr.scale_y
        self.debug = debug
        self.b = None
        if debug:
            self.b = Box(self.get_rect(), (255, 0, 0, 255))
            self.add(self.b)

    def _set_rotation(self, a):
        #a *= -1
        super(Sprite_Attachment, self)._set_rotation(-a)

    # def _set_image(self, img):
    #     print "BABAIKA"
    #     self.image_anchor = (img.width/2, img.height/2)
    #     super(Sprite_Attachment, self)._set_image(img)

    def set_new_attachment(self, image, attachment):
        self.name = attachment.name
        self.attachment_data = attachment
        #print "BABAIKA007"
        self.image_anchor = (image.width/2, image.height/2)
        self.image = image
        if self.debug:
            if self.b:
                self.b.kill()
            self.b = Box(self.get_rect(), (255, 0, 0, 255))
            self.add(self.b)
        #self.position = attachment.tsr.position
        #self.scale_x = attachment.tsr.scale_x
        #self.scale_y = attachment.tsr.scale_y
        #self.rotation = attachment.tsr.rotation

    def set_empty_image(self):
        self.image_anchor = (1,1)
        self.image = image.SolidColorImagePattern((0, 0, 0, 0)).create_image(2, 2)

    def set_tsr_by_named_pack(self, pack):
        self.position = pack.position
        self.scale_x = pack.scale_x
        self.scale_y = pack.scale_y
        self.rotation = pack.rotation
