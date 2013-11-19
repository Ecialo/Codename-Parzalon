__author__ = 'Ecialo'
# This code is so you can run the samples without installing the package
import sys
import os
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "Sprite"

import math

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos import euclid
from cocos.draw import Line
from cocos.actions.grid3d_actions import FlipY3D
from cocos.grid import Grid3D
import pyglet

## the following is in case we want to get the images
## from other directories:
# pyglet.resource.path.append("/data/other/directory")
# pyglet.resource.reindex()


def cross_angle(v1, v2):
    """
    Calculate cos between two lines
    """
    #Cos of angle between two hit lines
    angle = abs((v1.x * v2.x + v1.y * v2.y)/(abs(v1)*abs(v2)))
    #print angle
    return angle


def slash_rotation(sprite, v):
    cos = cross_angle(v, euclid.Vector2(1, 0))
    spin = (-1 if v.y < 0 else 1)*(1 if v.x >= 0 else -1)
    #zspin = (-1 if v.x < 0 else 1)*(-1 if v.y > 0 else 1)

    angle = math.acos(cos)*spin + (math.pi if v.x < 0 else 0)
    si = abs(math.sin(angle - math.pi/2))
    co = math.cos(angle)

    print math.degrees(angle), si, co

    x, y0, z = sprite.grid.get_original_vertex(1, 1)
    x, y1, z = sprite.grid.get_original_vertex(0, 0)

    if y0 > y1:
        # Normal Grid
        a = (0, 0)
        b = (0, 1)
        c = (1, 0)
        d = (1, 1)
        y = y0
    else:
        # Reversed Grid
        b = (0, 0)
        a = (0, 1)
        d = (1, 0)
        c = (1, 1)
        y = y1

    diff_y = y*si/2
    diff_z = (y*co)*si/2

    # bottom-left
    xx, yy, zz = sprite.grid.get_original_vertex(*a)
    sprite.grid.set_vertex(a[0], a[1], (xx, diff_y, z))

    # upper-left
    xx, yy, zz = sprite.grid.get_original_vertex(*b)
    sprite.grid.set_vertex(b[0], b[1], (xx, y-diff_y, z))

    # bottom-right
    xx, yy, zz = sprite.grid.get_original_vertex(*c)
    sprite.grid.set_vertex(c[0], c[1], (xx, diff_y, z))

    # upper-right
    xx, yy, zz = sprite.grid.get_original_vertex(*d)
    sprite.grid.set_vertex(d[0], d[1], (xx, y-diff_y, z))


    #sprite.rotation = -math.degrees(angle)


class TestLayer(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):

        #img = pyglet.image.SolidColorImagePattern((255, 255, 0, 255)).create_image(100, 100)

        super(TestLayer, self).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite('swing.png')
        self.p = euclid.Vector2(x/2, y/2)
        self.v = euclid.Vector2(0, 0)
        self.sprite.position = self.p
        grid = Grid3D()
        self.sprite.grid = grid
        self.sprite.grid.init(euclid.Point2(1, 1))
    #    self.sprite.grid.active = True
        self.line = Line(self.p, self.p + self.v, (255, 0, 0, 255))
        self.add(self.sprite)
        self.add(self.line, z=3)
        #self.sprite.do(FlipY3D())
        print self.sprite.grid

    #def on_mouse_motion(self, x, y, dx, dy):
    #    self.v = euclid.Vector2(x, y) - self.p
    #    self.line.end = self.p + self.v
    #    slash_rotation(self.sprite, self.v)
    #    #self.sprite.set_


def main():
    director.init(do_not_scale=True)
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene(test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
