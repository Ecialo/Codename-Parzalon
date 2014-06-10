# -*- coding: utf-8 -*-
__author__ = 'ecialo'
from .utility import binary_list

# Состояния автомата чтения из файла
NAME, LINE = binary_list(2)

# Размеры окна c текстом и отступ от портрета
DIALOG_WIDTH = 300          # По хорошему должны считаться динамически
DIALOG_HEIGHT = 128
STEP = 50

# Скорость показа текста
CHARS_PER_MINUTE = 10.0