# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
__author__ = "Ecialo"

from cocos import euclid as eu
import geometry as gm
import consts as con
import effects as eff
import box
import pyglet

consts = con.consts


def death(body_part):
    body_part.master.destroy()


class Body_Part(object):
    
    max_health = 10
    max_armor = 10
    
    def __init__(self, master, center, h_height, h_width, stab_priority, chop_priority, on_destroy_effects=[]):
        self.master = master

        self.health = self.max_health
        self.armor = self.max_armor

        self.on_destroy_effects = on_destroy_effects

        # Center relatively body
        p = gm.Point2(center.x - h_width, center.y - h_height)
        v = eu.Vector2(h_width * 2, h_height * 2)
        self.shape = gm.Rectangle(p, v)
        self.stab_priority = stab_priority
        self.chop_priority = chop_priority

        self.attached = None

    position = property(lambda self: self.master.master.from_self_to_global(self.shape.pc))
    horizontal_speed = property(lambda self: self.master.horizontal_speed)
    vertical_speed = property(lambda self: self.master.vertical_speed)

    def turn(self):
        c = self.shape.pc
        self.shape.pc = (-c[0], c[1])

    def set_pos(self, pos):
        self.shape.pc = (pos[0] * self.master.master.direction, pos[1])
        if self.attached is not None:
            self.attached.shell.shape.pc = self.shape.pc
        #print 11

    def take_hit(self, hit):
        """
        Body Part receive all effects from Hit
        and apply them to self
        """
        for effect in hit.effects:
            effect(self)
        if self.health <= 0:
            self.destroy()
        elif self.master.health <= 0:
            self.master.destroy()
        #print self.health, self.armor

    def get_on(self, item):
        if self.attached is not None:
            self.attached.drop()
        self.attached = item
        item.master = self
        item.shell.master = self.master
        self.master.body_parts.append(item.shell)

    def destroy(self):
        """
        Remove self and apply some effects
        """
        self.master.body_parts.remove(self)
        for effect in self.on_destroy_effects:
                effect(self)


class Chest(Body_Part):

    slot = con.CHEST

    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, 0), 40, 25, 2, 2,
                           [death])


class Head(Body_Part):

    slot = con.HEAD

    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, 57), 15, 20, 2, 2,
                           [death])


class Legs(Body_Part):

    slot = con.LEGS

    def __init__(self, master):
        Body_Part.__init__(self, master, eu.Vector2(0, -77), 33, 25, 2, 2,
                           [death])


class Body(object):

    anim = {}
    parts_pos = {}
    img = None
    base_speed = 0
    
    def __init__(self, master, body_parts):
        self.master = master
        self.speed = self.base_speed
        self.body_parts = map(lambda x: x(self), body_parts)
        self.health = sum(map(lambda x: x.max_health, body_parts))/2

    horizontal_speed = property(lambda self: self.master.horizontal_speed)
    vertical_speed = property(lambda self: self.master.vertical_speed)
        
    def destroy(self):

        """
        Destroy Body's master
        """

        self.master.destroy()

    def turn(self):
        map(lambda x: x.turn(), self.body_parts)
    
    def take_hit(self, hit):

        """
        1)Check is Hit hit any part of whole body
        2)If yes then recalculate coords of Hit to self base
        3)Sort Body Parts with priority whats depend from Hit type
        4)Check is first priority part intersects with Hit
        5)If yes take hit else get next and try again until Body Parts over
        """

        #Overlaps cshapes is not guarantee of successful attack
        #Need to compare shapes and traces
        #x, y = hit.end.x, hit.end.y
        #print hit.trace.p, hit.trace.v
        inner_p = self.master.from_global_to_self(hit.trace.p)
        inner_p = gm.Point2(inner_p.x, inner_p.y)
        inner_trace = hit.trace.copy()
        inner_trace.p = inner_p
        cleaved = False
        #inner_trace = gm.LineSegment2(inner_p, hit.trace.v)
        if hit.hit_pattern is con.CHOP:
            self.body_parts.sort(lambda a, b: a.chop_priority - b.chop_priority)
        else:
            self.body_parts.sort(lambda a, b: a.stab_priority - b.stab_priority)
        #print self.body_parts
        for part in self.body_parts:
            in_p = part.shape.intersect(inner_trace)
            if in_p is not None:
                p = self.master.from_self_to_global(part.shape.pc)
                eff.Blood().add_to_surface(p)
                part.take_hit(hit)
                #print hit.features, con.CLEAVE not in hit.features
                if con.CLEAVE not in hit.features:
                    break
                cleaved = True
        else:
            if not cleaved:
                return
        #print "Olollolo"
        if con.PENETRATE not in hit.features:
            hit.complete()

    def show_hitboxes(self):
        """
        Draw hitboxes of all Body Parts.
        """
        for bp in self.body_parts:
            color = (255, 0, 0, 255) if bp.slot - 100 < 0 else (0, 0, 255, 255)
            self.master.add(box.Box(bp.shape, color))

    def make_animation(self, anim_dict, filename):
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
            image = pyglet.image.load(name)
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
            image_sequence = map(lambda img: img, frames)
            pyg_anim = pyglet.image.Animation.from_image_sequence(image_sequence, 0.2, True)
            for i in range(len(duration_list)):
                pyg_anim.frames[i].duration = float(duration_list[i])
            anim_dict[name[0:len(name)-4]] = pyg_anim
            f.readline()
        f.close()

    def recalculate_body_part_position(self, arg):
        slot, pos = arg
        for body_part in self.body_parts:
            if body_part.slot is slot:
                body_part.set_pos(pos)
                break


class Human(Body):
    
    anim = {'walk': consts['img']['human'],
            'stay': consts['img']['human'],
            'jump': consts['img']['human'],
            'sit': consts['img']['human_sit']}
    parts_pos = {'walk': [(con.LEGS,(0, -77)), (con.CHEST,(0, 0)), (con.HEAD, (0, 57))],
                 'stay': [(con.LEGS,(0, -77)), (con.CHEST,(0, 0)), (con.HEAD, (0, 57))],
                 'jump': [(con.LEGS,(0, -77)), (con.CHEST,(0, 0)), (con.HEAD, (0, 57))],
                 'sit': [(con.LEGS,(0, -77)), (con.CHEST,(0, 0)), (con.HEAD, (0, 17))]}
    img = anim['stay']
    base_speed = consts['params']['human']['speed']

    def __init__(self, master):
        Body.__init__(self, master, [Chest, Head, Legs])
        self.make_animation(self.anim, 'human')