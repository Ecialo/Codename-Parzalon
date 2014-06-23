# -*- coding: utf-8 -*-
__author__ = 'Ecialo'
from cocos import layer

from .Animate import *
from task import *
from registry.controls import bindings
from registry.item import *


class Control(Task):

    bind = bindings
    pressed = False

    def __init__(self, master):
        Task.__init__(self, master)
        loc = self.master.get_ancestor(layer.ScrollableLayer)
        self.key = loc.loc_key_handler
        self.mouse = loc.loc_mouse_handler
        self.scroller = loc.scroller
        #self.static_objs = loc.static_collman
        #self.triggers = loc.scripts
        #print self.scroller

    def __call__(self, dt):
        #print self.bind
        if not self.pressed:
        #print "intsak", id(self.scroller)
            if self.key[self.bind['down']]:
                self.master.sit()
                Animate(self.master, 'sit')
                #print "intsak", id(self.scroller)
            else:
                hor_dir = self.key[self.bind['right']] - self.key[self.bind['left']]
                if self.key[self.bind['jump']] and self.master.on_ground:
                    self.master.jump()
                    Animate(self.master, 'jump')
                if hor_dir == 0:
                    self.master.stand()
                    Animate(self.master, 'stand')
                elif hor_dir != 0 and self.master.on_ground:
                    self.master.move(hor_dir)
                    Animate(self.master, 'walk')

            #Use items
            first_item_trigger = self.mouse[self.bind['first_hand']]
            alt = self.key[self.bind['alt_mode']]
            pos = self.mouse['pos']
            self.master.use_item(MAIN, first_item_trigger, [pos, alt])
            second_item_trigger = self.mouse[self.bind['second_hand']]
            self.master.use_item(SECONDARY, second_item_trigger, [pos, alt])

        # action = self.key[self.bind['action']]
        # if action:
        #     #print "CONTROLLER", self.key
        #     self.key[self.bind['action']] = False
        #     triggers = filter(lambda sc: 'trigger' in sc.properties,
        #                       self.triggers.iter_colliding(self.master))
        #     #print list(triggers)
        #     for tr in triggers:
        #         self.master.activate_trigger(tr)
        #
        # change = self.key[self.bind['change_weapon']]
        # if change:
        #     self.key[self.bind['change_weapon']] = False
        #     self.master.change_weapon()
        #
        # gain = self.key[self.bind['gain']]
        # if gain:
        #     self.key[self.bind['gain']] = False
        #     items = self.static_objs.objs_touching_point(*pos)
        #     for item in items:
        #         if not self.hands[1]:
        #             self.hands[1] = item
        #         if not self.hands[2]:
        #             self.hands[2] = item
        #         else:
        #             self.hands.append(item)
        #         self.master.put_item(item)
        #         item.get_up()

        inv = self.key[self.bind['inventory']]
        # if inv:
        #     self.master.drop()
        # self.key[self.bind['inventory']] = False
        if inv and not self.pressed:
            self.key[self.bind['inventory']] = False
            self.master.open()
            self.pressed = True
        elif inv and self.pressed:
            self.key[self.bind['inventory']] = False
            self.master.close()
            self.pressed = False
        else:
            pass

        #cx, cy = self.master.position
        #print cx, cy
        self.scroller.set_focus(*self.master.position)