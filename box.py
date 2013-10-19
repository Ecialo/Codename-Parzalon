__author__ = 'Ecialo'

import cocos
from cocos.director import director
from cocos.draw import *
import geometry as gm
import cocos.euclid as eu
#import pyglet


class Box(Canvas):
    r = parameter()
    stroke_width = parameter()
    color = parameter()

    def __init__(self, rectangular, color, stroke_width=1):
        super(Box, self).__init__()
        self.r = rectangular
        self.hw, self.hh = self.r.v/2
        self.color = color
        self.stroke_width = stroke_width
        self.schedule(self.update)

    def update(self, dt):
        self.position = self.r.pc

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







class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        s = cocos.sprite.Sprite('chelovek_v2.png')
        s.position = (300, 300)
        r = gm.Rectangle(eu.Vector2(0, 0), eu.Vector2(15, 15))
        r.pc = (0, 0)
        s.add(Box(r, (255, 0, 0, 255)))
        ac = cocos.actions.MoveTo((500, 500))
        self.add(s)
        #s.do(ac)

        self.schedule(lambda x: 0)

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
