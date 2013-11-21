__author__ = 'Ecialo'
# An advanced setup script to create multiple executables and demonstrate a few
# of the features available to setup scripts
#
# hello.py is a very simple "Hello, world" type script which also displays the
# environment in which the script runs
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

#import sys
#sys.argv.append('build')
#if sys.platform == "win32":
#    base = "Win32GUI"
from cx_Freeze import setup, Executable

setup(
        name = "simple_PyQt4",
        version = "0.1",
        description = "Sample cx_Freeze PyQt4 script",
        options = {"build_exe" : {"include_files" : ['5z1KX.png', 'stand.png', 'knife.png',
                                                     'map01.tmx', 'map02.tmx', 'mytileset_01.png',
                                                     'sword.png', 'sit.png', 'swing.png', 'twister.png',
                                                     'bullet.png', 'fuzeja.png', 'helm.png', 'inventory.png',
                                                     'walk.png', 'jump.png', 'human', 'hero',
                                                     'draw_texture.png', 'fire.png']}},
        executables = [Executable("codename-Parzalon.py")])


#['5z1KX.png', 'chelovek_v2.png', 'knife.png',
#'map01.tmx', 'mytileset_01.png', 'sword.png']