# -*- coding: utf-8 -*-
__author__ = 'ecialo'
from script import Script
from actor import Actor
from registry import BASE
from registry.group import HERO


def spawn_unit(map_object, environment, position):
    pos = position
    unit_name = map_object['unit_name']
    un_par = BASE[unit_name]
    unit = Actor(un_par['body'])
    map(lambda x: unit.put_item(x()(environment)), un_par['items'])
    if un_par['brain'].fight_group is HERO and environment.hero is None:
        environment.hero = unit
    elif un_par['brain'].fight_group is HERO and environment.hero is not None:
        environment.hero.destroy()
        environment.hero = unit
    unit.launcher.push_handlers(environment)
    environment.actors.append(unit)
    environment.add(unit, z=2)
    unit.b2body.position = pos
    unit.do(un_par['brain']())


def spawn_item(map_object, enviroment):
    pass


class Spawn(Script):

    spawn_type = {'unit': spawn_unit,
                  'item': spawn_item}

    def __init__(self, map_object, environment):
        super(Spawn, self).__init__(map_object, environment)

    def run(self, position):
        map_object = self.map_object
        self.spawn_type[map_object['spawn_type']](map_object, self.environment, position)
