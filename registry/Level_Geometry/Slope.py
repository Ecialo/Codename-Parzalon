# -*- coding: utf-8 -*-
__author__ = 'ecialo'
import Box2D as b2
from registry.box2d import B2SMTH, B2LEVEL, B2EVERY


def Slope(cell, environment):
    x, y = cell.i, cell.j
    sx, sy, dx, dy = map(float, cell['slope'].split())
    shape = b2.b2EdgeShape(vertex1=(x+sx, y+sy), vertex2 = (x+sx+dx, y+sy+dy))
    lvl = environment.b2level
    lvl.CreateFixture(shape=shape, userData=cell)
    lvl.fixtures[-1].filterData.categoryBits = B2SMTH | B2LEVEL
    lvl.fixtures[-1].filterData.maskBits = B2EVERY