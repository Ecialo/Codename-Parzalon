# -*- coding: utf-8 -*-
__author__ = "Ecialo"
from cocos.director import director
from menu import GameMenu

from registry.window import *
#import cProfile        # Оставим профайлер. Один раз он уже пригодился.


def main():
    director.init(**window)
    menu = GameMenu()
    menu.start_game()

if __name__ == "__main__":
    main()
#o = open("parz.pyprof", 'w')
#cProfile.run('main()', "parz.pyprof")
#o.close()
