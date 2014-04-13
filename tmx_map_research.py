#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Ecialo"
__date__ ="$28.08.2013 17:00:53$"
import cocos
from cocos.director import *
from cocos import tiles

if __name__ == "__main__":
    director.init(width=800, height=600, do_not_scale=True)
    mp = tiles.load('map01.tmx')
    force = mp['Player Level']
    objs = mp['Scripts']
    print objs[0].midbottom