# -*- coding: utf-8 -*-
__author__ = 'ecialo'
from script import Script
from registry import BASE


def spawn_unit(map_object, environment):
    spawned_unit = None
    if map_object['unit_name'] == 'Parzalon':
        environment.hero = spawned_unit


def spawn_item(map_object, enviroment):
    pass


class Spawn(Script):

    spawn_type = {'unit': spawn_unit,
                  'item': spawn_item}

    def __init__(self, map_object, environment):
        super(Spawn, self).__init__(map_object, environment)

    def run(self, position):
        map_object = self.map_object
        self.spawn_type[map_object['spawn_type']](map_object, self.environment)
