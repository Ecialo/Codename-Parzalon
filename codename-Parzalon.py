# -*- coding: utf-8 -*-
__author__ = "Ecialo"
from cocos.director import director
from menu import GameMenu

import consts
#from level import Level
from registry.Levels import levels_base
#import cProfile

#consts = con.consts


def main():
    director.init(**consts.window)
    lvl = levels_base['Test_Level']
    lvl.run()
    # menu = GameMenu()
    # menu.start_game()

if __name__ == "__main__":
    main()
#o = open("parz.pyprof", 'w')
#cProfile.run('main()', "parz.pyprof")
#o.close()
