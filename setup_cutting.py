__author__ = 'Ecialo'
from cx_Freeze import setup, Executable
setup(
        name = "simple_PyQt4",
        version = "0.1",
        description = "Sample cx_Freeze PyQt4 script",
        options = {"build_exe" : {"include_files" : ['draw_texture.png']}},
        executables = [Executable("codename-Parzalon.py")])
