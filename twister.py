__author__ = 'Ecialo'

from pyglet.image import Animation
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
            #print "LAUNCH"
            master.collided = True

        def mast_emmiter(dt):
            if master.collided:
                #print "DEATH"
                hit_z = hits.Invisible_Hit_Zone(master.launcher, master.cshape.rx*2 + 200, master.cshape.ry*2 + 200,
                                                eu.Vector2(0, 0), 0, master.position,
                                                [on_h.damage(value)])
                master.launcher.launch(hit_z)
                master.collided = False

        master.collided = False
        master.schedule_interval(mast_emmiter, 0.25)
        return targ_on_collide_damage
    return mast_on_collide_damage


class Skull(bodies.Body_Part):

    slot = con.HEAD

    def __init__(self, master):
        bodies.Body_Part.__init__(self, master, eu.Vector2(0, 0), 15, 15, 1, 1,
                                  [bodies.death])


class Twister_Body(bodies.Body):

    anim = {'walk': Animation.from_image_sequence([consts['img']['twister']], 0.0),
            'stand': Animation.from_image_sequence([consts['img']['twister']], 0.0),
            'jump': Animation.from_image_sequence([consts['img']['twister']], 0.0)}

    parts_pos = {'walk': [(con.HEAD, (0, 0))],
                 'stand': [(con.HEAD, (0, 0))],
                 'jump': [(con.HEAD, (0, 0))]}
    img = consts['img']['twister']
    base_speed = consts['params']['human']['speed']

    def __init__(self, master):
        bodies.Body.__init__(self, master,
                             [Skull], 'twister_body',
                             [on_collide_damage(1)])
        self.skull = sprite.Sprite(consts['img']['skull'])
        self.master.add(self.skull)


class Stalk(brains.Task):

    def __init__(self, master, target):
        brains.Task.__init__(self, master)
        self.target = target

    def __call__(self, dt):
        if self.target.fight_group > 0:
            dst = self.target.cshape.center.x - self.master.cshape.center.x
            d = dst/abs(dst) if abs(dst) != 0 else 0
            #print dst
            self.master.walk(self.master.direction)
            if self.master.wall & (con.LEFT | con.RIGHT):
                self.master.push_inst_task(brains.Jump(self.master))
            if d != self.master.direction:
                self.master.push_inst_task(brains.Turn(self.master))
        else:
            return brains.COMPLETE


class Twister_Fight(brains.Task):

    def __init__(self, master, brain, target):
        brains.Task.__init__(self, master)
        self.brain = brain
        self.target = target

    def __call__(self, dt):
        if self.target.fight_group > 0:
            dst = self.target.cshape.center.x - self.master.cshape.center.x
            d = dst/abs(dst) if abs(dst) != 0 else 0
            if abs(dst) > 300:
                #print "Like a sir"
                hand = self.master.choose_free_hand()
                if hand:
                    self.master.push_inst_task(brains.Aim(self.master, hand, self.target))
            else:
                self.master.push_inst_task(Stalk(self.master, self.target))
        else:
            self.master.push_task(brains.Stand(self.master))
            self.brain.observed_units.remove(self.target)
            return brains.COMPLETE


class Skull_Move(brains.Task):

    def __init__(self, master, v, priority):
        brains.Task.__init__(self, master, priority)
        self.v = v

    def __call__(self, dt):
        self.master.push_task(brains.Body_Part_Move_On(self.master, self.v, con.HEAD))
        self.body.skull.position += self.v
        return brains.COMPLETE


class Twister_Mind(brains.Primitive_AI):

    def start(self):
        brains.Primitive_AI.start(self)

    def sensing(self):
        #print self.task_manager.tasks
        self.clear_vision()
        for obj in self.vision.objs_near(self.master, self.range_of_vision):
            if obj.fight_group < consts['slash_fight_group']:
                self.visible_actors.append(obj)
            elif obj.fight_group < consts['missile_fight_group']:
                self.visible_hits.append(obj)
            else:
                pass
        for enemy in filter(lambda x: self.is_enemy(x), self.visible_actors):
            if enemy not in self.observed_units:
                print 123, enemy
                self.task_manager.push_task(Twister_Fight(self.master, self, enemy))
                self.observed_units.add(enemy)


class Twister_Shard(items.Usage_Item):

    def __init__(self):
        img = consts['img']['shard']
        first_usage = usages.Shoot([on_h.damage(1)], img)
        second_usage = None
        items.Usage_Item.__init__(self, img, first_usage, second_usage,
                                  [items.length(1), items.fire_rate(0.5), items.ammo(1)])