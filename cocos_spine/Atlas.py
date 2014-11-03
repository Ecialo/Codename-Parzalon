__author__ = 'Ecialo'
# -*- coding: utf-8 -*-
import pyglet
import os
false = False
true = True


class Atlas(object):

    def __init__(self, file):
        self.atlas = pyglet.image.atlas.TextureBin(1024, 1024)
        self.lib = {}
        self.region_lib = {}
        self.load(file)
        self.preprocess()

    def load(self, file):
        if not file:
            raise Exception('input cannot be null.')

        st_filename, st_metadata, st_name, st_data = xrange(4)
        state = st_name

        def clean(s):
            return s.strip().rstrip()

        with open(os.path.realpath(file), 'r') as fh:
            image = None
            file_name = None
            file_data = {}
            region_name = None
            region_data = {}
            for line in fh:
                value = clean(line)
                #print value, state
                while True:
                    if state is st_filename:
                        file_name = value
                        image = pyglet.image.load('cocos_spine/'+file_name) #TODO исправить на корректные пути
                        state = st_metadata
                    elif state is st_metadata:
                        if ':' in value:
                            #name, data = map(clean, value.split(':'))
                            #file_data[name] = data
                            #print name, data
                            pass
                        else:
                            state = st_name
                            continue
                    elif state is st_name:
                        if value:
                            region_name = value
                            state = st_data
                            region_data = {}
                        else:
                            if file_name:
                                self.lib[file_name] = file_data
                                file_data = {}
                                region_data = {}
                            state = st_filename
                    elif state is st_data:
                        if ':' in value:
                            name, data = map(clean, value.split(':'))
                            #TODO: too bad! do not use eval!
                            #print "maybe"
                            region_data[name] = eval("("+data+")")
                            #print "not"
                        else:
                            #print "start_apply_region"
                            region_data['region'] = self.get_region(image, region_data)
                            #print "NOW"
                            file_data[region_name] = region_data
                            #print "NOWW"
                            state = st_name
                            continue
                    break
        region_data['region'] = self.get_region(image, region_data)
        file_data[region_name] = region_data
        self.lib[file_name] = file_data

    def preprocess(self):
        for file_data in self.lib.itervalues():
            for region_name in file_data:
                #print region_name
                #print file_data[region_name]
                self.region_lib[region_name] = file_data[region_name]['region']
        #print self.region_lib['tail05']

    def get_attachment_region(self, name):
        return self.region_lib[name]

    def get_region(self, image, region_data):
        x, y = region_data['xy']        # left top
        width, height = region_data['size']
        h = image.height
        #w = image.width
        #x = w - x
        y = h - height - y
        #print y, h, h + y
        #print h - y
        #x, y = 0, 0
        #width, height = 672, h/2
        region = image.get_region(x, y, width, height)
        #print region
        att = self.atlas.add(region)
        #print att
        return att


def main():

    from cocos import layer
    from cocos import scene
    from cocos import sprite
    from cocos.director import director
    from Attachment import Box
    from cocos.rect import Rect

    director.init(1024, 1024)
    red = (255, 0, 0, 255)
    class TestLayer(layer.Layer):

        is_event_handler = True

        def __init__(self):
            c = Rect(0, 0, 10,10)
            b = Box(c, red)
            super(TestLayer, self).__init__()
            self.a = Atlas('./cocos_spine/skeleton.atlas')
            self.names = sorted(self.a.region_lib.keys())
            self.i = 17
            print self.names[self.i]
            self.sprite = sprite.Sprite(self.a.get_attachment_region(self.names[self.i]))
            #self.sprite.scale_x = 0.5
            #self.sprite.scale_y = 0.25
            self.b = Box(self.sprite.get_rect(), red)
            self.sprite.add(self.b)
            self.sprite.position = (512, 512)
            self.add(self.sprite, z=1)
            self.add(b, z=1)

        def on_key_press(self, symbol, modifers):
            self.i += 1
            self.i %= len(self.names)
            image = self.a.get_attachment_region(self.names[self.i])
            print self.names[self.i]
            self.sprite.image_anchor = (image.width/2, image.height/2)
            self.sprite.image = image
            #self.sprite.position = (512, 512)
            #self.sprite.anchor = (self.sprite.image.width/2, self.sprite.image.height/2)
            self.b.kill()
            #self.sprite.kill()
            #self.sprite = sprite.Sprite(self.a.get_attachment_region(self.names[self.i]))
            #self.add(self.sprite)
            #self.sprite.position = (512, 512)
            self.b = Box(self.sprite.get_rect(), red)
            self.sprite.add(self.b, z=5)





    scene = scene.Scene(TestLayer())
    director.run(scene)


    #sd = Skeleton_Data('./data/dragon.json', './data/dragon.atlas')

if __name__ == "__main__":
    main()