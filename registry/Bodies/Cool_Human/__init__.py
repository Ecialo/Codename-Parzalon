# -*- coding: utf-8 -*-
__author__ = 'ecialo'

from body import Cool_Body
from registry.utility import module_path_to_os_path

prefix = module_path_to_os_path(__name__)


class Cool_Human(Cool_Body):

    skeleton_json = prefix + "skeleton.json"
    skeleton_atlas = prefix + "skeleton.atlas"

    params = \
    {
        'acceleration': 0.5,
        'max_speed': 21.0,
        'jump_height': 6.0
    }