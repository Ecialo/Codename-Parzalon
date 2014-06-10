# -*- coding: utf-8 -*-
__author__ = "Ecialo"
from cocos.director import director
from menu import GameMenu

from registry.window import *
#from registry.Levels import levels_base
#import cProfile


def main():
    director.init(**window)
    # lvl = levels_base['Test_Level']
    # print lvl
    # lvl.run()
    menu = GameMenu()
    menu.start_game()

if __name__ == "__main__":
    main()
#o = open("parz.pyprof", 'w')
#cProfile.run('main()', "parz.pyprof")
#o.close()
