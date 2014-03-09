__author__ = "Ecialo"
#######
from cocos.director import director
from menu import GameMenu

import consts as con
import cProfile

consts = con.consts


def main():
    director.init(**consts['window'])
    menu = GameMenu()
    menu.start_game()

if __name__ == "__main__":
    main()
#o = open("parz.pyprof", 'w')
#cProfile.run('main()', "parz.pyprof")
#o.close()
