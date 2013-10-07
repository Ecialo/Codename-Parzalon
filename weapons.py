# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"

import items
import usages
import consts as con
import on_hit_effects as onh

consts = con.consts


class Sword(items.Weapon):

    def __init__(self, environment):
        img = consts['img']['weapon']
        first_usage = usages.Chop([onh.damage(5), onh.knock_back(100)])
        second_usage = usages.Stab([onh.damage(7)])
        items.Weapon.__init__(self, img, 100, first_usage, second_usage, environment)


class Knife(items.Weapon):

    def __init__(self, environment):
        img = consts['img']['knife']
        first_usage = usages.Chop([onh.damage(1)])
        second_usage = usages.Throw([onh.damage(1)])
        items.Weapon.__init__(self, img, 20, first_usage, second_usage, environment)