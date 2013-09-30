__author__ = "Ecialo"

from cocos.director import director

import level
import consts as con

consts = con.consts


def main():
    director.init(**consts['window'])
    lvl = level.create_level('map01.tmx')
    director.run(lvl)


if __name__ == "__main__":
    main()
