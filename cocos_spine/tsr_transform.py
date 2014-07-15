__author__ = 'Pavgran'

import math


def tsr_transform(par_tsr, child_tsr):
    pos, scale_x, scale_y, rot = child_tsr
    par_pos, par_scale_x, par_scale_y, par_rot = par_tsr
    cos = math.cos(math.radians(par_rot))
    sin = math.sin(math.radians(par_rot))
    x = (pos[0]*cos*par_scale_x - pos[1]*sin*par_scale_y + par_pos[0])
    y = (pos[0]*sin*par_scale_x + pos[1]*cos*par_scale_y + par_pos[1])
    new_pos = (x, y)
    new_scale_x = scale_x + par_scale_x - 1
    new_scale_y = scale_y + par_scale_y - 1
    new_rot = (rot + par_rot)# % 360)# - 180
    return (new_pos, new_scale_x, new_scale_y, new_rot)
