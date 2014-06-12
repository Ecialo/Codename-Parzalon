# -*- coding: utf-8 -*-
import effects as eff

__author__ = "Ecialo"

import geometry as gm
from registry.utility import EMPTY_LIST
from registry.group import CHOP, PENETRATE, CLEAVE
import box
import pyglet


class Body(object):

    anim = {}
    parts_pos = {}
    img = None
    base_speed = 0
    
    def __init__(self, master, body_parts, body_name, on_collide_effects=EMPTY_LIST):
        self.master = master
        self.speed = self.base_speed
        self.body_parts = map(lambda x: x(self), body_parts)
        self.on_collide_effects = map(lambda x: x(self.master), on_collide_effects)
        self.max_health = sum(map(lambda x: x.max_health, filter(lambda x: x.slot < 100, body_parts)))/2
        self.health = self.max_health
        self.body_name = body_name
        
    def destroy(self):

        """
        Destroy Body's master
        """

        self.master.destroy()

    def turn(self):
        for animations in self.anim:
            for i in range(len(self.anim[animations].frames)):
                self.anim[animations].frames[i].image = \
                    self.anim[animations].frames[i].image.get_texture().get_transform(flip_x=True)
        map(lambda x: x.turn(), self.body_parts)

    def take_hit(self, hit):

        """
        1)Check is Hit hit any part of whole body
        2)If yes then recalculate coords of Hit to self base
        3)Sort Body Parts with priority whats depend from Hit type
        4)Check is first priority part intersects with Hit
        5)If yes take hit else get next and try again until Body Parts over
        """

        inner_p = self.master.from_global_to_self(hit.trace.p)
        inner_p = gm.Point2(inner_p.x, inner_p.y)
        inner_trace = hit.trace.copy()
        inner_trace.p = inner_p
        cleaved = False
        if CHOP in hit.features:
            self.body_parts.sort(lambda a, b: a.chop_priority - b.chop_priority)
        else:
            self.body_parts.sort(lambda a, b: a.stab_priority - b.stab_priority)
        for part in self.body_parts:
            in_p = part.shape.intersect(inner_trace)
            if in_p is not None:
                p = self.master.from_self_to_global(part.shape.pc)
                eff.Blood().add_to_surface(p)
                part.collide(hit)
                if CLEAVE not in hit.features:
                    break
                cleaved = True
        else:
            if not cleaved:
                return
        if PENETRATE not in hit.features:
            hit.complete()

    def show_hitboxes(self):
        """
        Draw hitboxes of all Body Parts.
        """
        for bp in self.body_parts:
            color = (255, 0, 0, 255) if bp.slot - 100 < 0 else (0, 0, 255, 255)
            self.master.add(box.Box(bp.shape, color))

    def recalculate_body_part_position(self, arg):
        slot, pos = arg
        for body_part in self.body_parts:
            if body_part.slot is slot:
                body_part.set_pos(pos)
                break

    def make_animation(self, anim, filename, path):
        filename = path + filename.lower()
        f = open(filename)
        while 1:
            name = f.readline()
            if not name:
                break
            name = name[0:len(name)-1]
            frame_height = int(f.readline())
            frame_width = int(f.readline())
            duration_list = []
            l = f.readline()
            s = l.split(' ')
            s[len(s)-1] = s[len(s)-1][0:len(s[len(s)-1])-1]
            for i in range(len(s)):
                duration_list.append(float(s[i]))
            image = pyglet.image.load(path + name)
            frames = []
            start = image.height
            i = 1
            while start >= frame_height:
                left_border = 0
                bottom_border = image.height - frame_height*i
                end = image.width
                while end >= frame_width:
                    cut = image.get_region(left_border, bottom_border, frame_width, frame_height)
                    frames.append(cut)
                    left_border += frame_width
                    end -= frame_width
                start -= frame_height
                i += 1
            pyg_anim = pyglet.image.Animation.from_image_sequence(frames, 0.2, False)
            for i in range(len(duration_list)):
                pyg_anim.frames[i].duration = float(duration_list[i])
            anim[name[0:len(name)-4]] = pyg_anim
            f.readline()
        f.close()