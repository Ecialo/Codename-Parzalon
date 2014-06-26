# -*- coding: utf-8 -*-
__author__ = 'ecialo'


def obstacle_coroutine():
    current_environment = None
    #max_x = -1
    #max_y = -1
    cell_column = []
    while True:
        cell, environment = (yield)
        if environment is not current_environment:
            current_environment = environment
            last_cell = current_environment.rect_map[-1][-1]
            max_x, max_y = last_cell.i, last_cell.j
        cell_column.append(cell)
        # if cell.i == max_x and cell.j == max_y or cell.i != cell_column[-1] or abs(cell.j - cell_column[-1]) > 1:
        #     create_column(cell.i, len(cell_column), environment)


def Obsctacle(cell, environment):
    Obsctacle.worker.send((cell, environment))

Obsctacle.worker = obstacle_coroutine()
next(Obsctacle.worker)