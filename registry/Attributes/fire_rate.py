# -*- coding: utf-8 -*-
__author__ = 'ecialo'


def fire_rate(time_between_shots):
    def add_fire_rate(master):
        def reload_weapon(dt):
            if master.cur_reload > 0.0:
                master.cur_reload -= dt
                if master.cur_reload <= 0.0:
                    master.cur_reload = 0.0
                    master.available = True
        master.reload_time = time_between_shots
        master.cur_reload = 0.0
        master.item_update = reload_weapon
    return add_fire_rate
