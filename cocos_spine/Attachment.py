__author__ = 'Pavgran'


class Attachment(object):

    def __init__(self, name=None, x=0, y=0, scaleX=1, scaleY=1, rotation=0, width=0, height=0):
        self.name = name
        self.x = x
        self.y = y
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.rotation = rotation
        self.width = width
        self.height = height
