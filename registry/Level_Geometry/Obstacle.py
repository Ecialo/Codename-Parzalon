# -*- coding: utf-8 -*-
__author__ = 'ecialo'
import Box2D as b2
from registry.box2d import B2LEVEL, B2SMTH, B2EVERY
from registry.box2d import NO_ROTATION, HALF_TILE

#
# def obstacle_coroutine():
#     current_environment = None
#     #max_x = -1
#     #max_y = -1
#     cell_column = []
#     while True:
#         cell, environment = (yield)
#         if environment is not current_environment:
#             current_environment = environment
#             last_cell = current_environment.rect_map[-1][-1]
#             max_x, max_y = last_cell.i, last_cell.j
#         cell_column.append(cell)
#         # if cell.i == max_x and cell.j == max_y or cell.i != cell_column[-1] or abs(cell.j - cell_column[-1]) > 1:
#         #     create_column(cell.i, len(cell_column), environment)
#
#
# def Obsctacle(cell, environment):
#     Obsctacle.worker.send((cell, environment))
#
# Obsctacle.worker = obstacle_coroutine()
# next(Obsctacle.worker)


def Obstacle(cell, environment):
    x, y = cell.i, cell.j
    shape = b2.b2PolygonShape()
    shape.SetAsBox(HALF_TILE, HALF_TILE, (x+HALF_TILE, y+HALF_TILE), NO_ROTATION)
    lvl = environment.b2level
    lvl.CreateFixture(shape=shape, userData=cell)
    lvl.fixtures[-1].filterData.categoryBits = B2SMTH | B2LEVEL
    lvl.fixtures[-1].filterData.maskBits = B2EVERY