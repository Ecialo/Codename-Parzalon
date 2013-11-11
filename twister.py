__author__ = 'Ecialo'

from cocos import euclid as eu
from cocos import sprite
import bodies
import brains
import items
import usages
import on_hit_effects as on_h
import consts as con
import hits

consts = con.consts


def on_collide_damage(value):
    def mast_on_collide_damage(master):
        def targ_on_collide_damage(target):
            hit_z = hits.Invisible_Hit_Zone(master.launcher, master.cshape.rx*2 + 200, master.cshape.ry*2 + 200,
                                            eu.Vector2(0, 0), 0, master.position,
                                            [on_h.damage(value)])
            master.launcher.launch(hit_z)
        return targ_on_collide_damage
    return mast_on_collide_damage


class Skull(bodies.Body_Part):

    slot = con.HEAD

    def __init__(self, master):
        bodies.Body_Part.__init__(self, master, eu.Vector2(0, 0), 15, 15, 1, 1,
                                  [bodies.death])


class Twister_Body(bodies.Body):

    anim = {'walk': consts['img']['twister'],
            'stand': consts['img']['twister'],
            'jump': consts['img']['twister']}

    parts_pos = {'walk': [(con.HEAD, (0, 0))],
                 'stand': [(con.HEAD, (0, 0))],
                 'jump': [(con.HEAD, (0, 0))]}
    img = consts['img']['twister']
    base_speed = consts['params']['human']['speed']

    def __init__(self, master):
        bodies.Body.__init__(self, master,
                             [Skull],
                             [on_collide_damage(3)])
        self.skull = sprite.Sprite(consts['img']['skull'])
        self.add(self.skull)


class Wait_And_Stalk(brains.Task):

    def __init__(self, master, brain):
        brains.Task.__init__(self, master, 0)
        self.brain = brain

    def __call__(self, dt):
        #print 111
        for unit_wd in self.brain.visible_actors_wd:
            unit, dst = unit_wd
            if self.brain.is_enemy(unit):
                self.master.push_task(Stalk(self.master, self.brain, unit))


class Stalk(brains.Task):
    def __init__(self, master, brain, target):
        brains.Task.__init__(self, master, 1)
        self.brain = brain
        self.target = target

    def __call__(self, dt):
        if self.target.fight_group > 0:
            dst = self.target.cshape.center.x - self.master.cshape.center.x
            d = dst/abs(dst) if abs(dst) != 0 else 0
            #print dst
            if d != self.master.direction:
                self.master.push_task(brains.Turn(self.master, 11))
            self.master.walk(self.master.direction)
            if self.master.wall & (con.LEFT | con.RIGHT):
                self.master.push_task(brains.Jump(self.master, 98))
        else:
            #print 1234
            self.master.push_task(brains.Stand(self.master, 1))
            return brains.COMPLETE


class Skull_Move(brains.Task):

    def __init__(self, master, v, priority):
        brains.Task.__init__(self, master, priority)
        self.v = v

    def __call__(self, dt):
        self.master.push_task(brains.Body_Part_Move_On(self.master, self.v, con.HEAD, self.priority))
        self.body.skull.position += self.v
        return brains.COMPLETE


class Twister_Mind(brains.Primitive_AI):

    def start(self):
        brains.Primitive_AI.start(self)
        self.task_manager.push_task(Wait_And_Stalk(self.master, self))


class Twister_Shard(items.Usage_Item):

    def __init__(self):
        img = None
        first_usage = usages.Shoot([on_h.damage(1)], img)
        second_usage = None
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(1), items.ammo(99)])