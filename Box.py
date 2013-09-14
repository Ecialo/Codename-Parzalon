__author__ = 'Ecialo'

import cocos
from cocos.director import director
from cocos.draw import *
import geometry as gm
import cocos.euclid as eu
#import pyglet


class Box(Canvas):
    rectangular = parameter()
    stroke_width = parameter()
    color = parameter()

    def __init__(self, rectangular, color, stroke_width=1):
        super(Box, self).__init__()
        self.r = rectangular
        self.color = color
        self.stroke_width = stroke_width

    def render(self):
        self.set_color(self.color)
        self.set_stroke_width(self.stroke_width)

        self.move_to(self.r.plb)
        self.line_to(self.r.plt)

        self.move_to(self.r.plt)
        self.line_to(self.r.prt)

        self.move_to(self.r.prt)
        self.line_to(self.r.prb)

        self.move_to(self.r.prb)
        self.line_to(self.r.plb)







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
