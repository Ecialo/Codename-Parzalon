__author__ = "Ecialo"

from cocos.director import director

from level import Level
import consts as con
import cProfile

consts = con.consts


def main():
    director.init(**consts['window'])
    lvl = Level((0, 0), [['map01.tmx'], ['map02.tmx']])
    lvl.run()


if __name__ == "__main__":
    main()
#o = open("parz.pyprof", 'w')
#cProfile.run('main()', "parz.pyprof")
#o.close()
