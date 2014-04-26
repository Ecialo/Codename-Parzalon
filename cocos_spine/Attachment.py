__author__ = 'Pavgran'

from cocos import sprite


class Attachment(object):

    def __init__(self, name=None, x=0, y=0, scaleX=1, scaleY=1, rotation=0, width=0, height=0):
        self.name = name
        self.position = (x, y)
        self.scale_x = scaleX
        self.scale_y = scaleY
        self.rotation = rotation
        self.width = width
        self.height = height


class Sprite_Attachment(sprite.Sprite):

    def __init__(self, image, attachment):
        self.name = attachment.name
        self.attachment_data = attachment
        position = attachment.position
        image = image           # We must place here image from atlas
        super(Sprite_Attachment, self).__init__(image, position, attachment.rotation)
        self.scale_x = attachment.scale_x
        self.scale_y = attachment.scale_y
