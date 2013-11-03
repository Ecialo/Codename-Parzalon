__author__ = 'Ecialo'

from cocos import euclid as eu
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
            hit_z = hits.Invisible_Hit_Zone(master, master.cshape.half_width*2, master.cshape.half_height*2,
                                            eu.Vector2(0, 0), 0, master.position,
                                            [on_h.damage(value)])
            master.launcher.launch(hit_z)
        return targ_on_collide_damage
    return mast_on_collide_damage


class Skull(bodies.Body_Part):

    def __init__(self, master):
        bodies.Body_Part.__init__(self, master, eu.Vector2(0, 0), 15, 15, 1, 1,
                                  [bodies.death],
                                  [on_collide_damage(3)])


class Twister_Body(bodies.Body):

    anim = {'walk': consts['img']['twister'],
            'stay': consts['img']['twister']}
    img = consts['img']['twister']
    base_speed = consts['params']['human']['speed']

    def __init__(self, master):
        bodies.Body.__init__(self, master,
                             [Skull])


class Twister_Mind(brains.Enemy_Brain):
    pass


class Twister_Shard(items.Usage_Item):

    def __init__(self):
        img = None
        first_usage = usages.Shoot([on_h.damage(1)], img)
        second_usage = None
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(1), items.ammo(99)])