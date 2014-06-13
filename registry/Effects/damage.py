# -*- coding: utf-8 -*-
__author__ = 'Ecialo'


def damage(value):
    def mast_damage(master):
        def fab_damage(body_part):
            if body_part.armor > value:
                body_part.armor -= value
            else:
                body_part.health -= value
                body_part.master.health -= value
            body_part.master.master.dispatch_event("on_take_damage", body_part)
        return fab_damage
    return mast_damage
