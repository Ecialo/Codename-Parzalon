# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

from math import sqrt
from box2d import GRAVITY

TILE_SIZE_IN_PIXELS = 32


def tiles_to_pixels(tiles):
    if hasattr(tiles, '__iter__'):
        return type(tiles)([tiles_to_pixels(x) for x in tiles])
    else:
        return tiles*1.0*TILE_SIZE_IN_PIXELS


def pixels_to_tiles(pixels):
    if hasattr(pixels, '__iter__'):
        return type(pixels)([pixels_to_tiles(x) for x in pixels])
    else:
        return pixels*1.0/TILE_SIZE_IN_PIXELS


def jump_height_to_jump_speed(height_in_tiles):
    return sqrt(2*GRAVITY*height_in_tiles)
