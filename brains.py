# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"

import random as rnd

import pyglet
from cocos import actions as ac
from cocos import euclid as eu
from cocos import layer
from collections import deque

import consts as con

consts = con.consts

COMPLETE = True
TASK_CHANGE_TIME = 0.1
SECONDARY, MAIN = xrange(2)


def cross_hit_trace(hit):
    v = hit.trace.v
    nv = v.cross()
    if v.x >= 0 and v.y < 0 or v.x < 0 and v.y < 0:
        return nv
    else:
        return -nv


def _set_rec(self, value):
    self.master.recovery = value


def Animate(master, name):
    if master.state != name:
        master.state = name
        master.image = master.body.anim[name]


class Task(object):

    #hands = property(lambda self: self.master.hands)
    environment = None

    def __init__(self, master, time=None):
        self.master = master
        self.time = time

    def __call__(self, dt):
        if self.time is not None:
            self.time -= dt
            return COMPLETE if self.time <= 0.0 else None


class Pause(Task):
    pass


class Approaches(Task):

    def __init__(self, master, brain, target):
        Task.__init__(self, master)
        self.brain = brain
        self.target = target

    def __call__(self, dt):
        #print "Approach", self.target
        #print self.brain.task_manager.tasks
        Animate(self.master, 'walk')
        if self.target.fight_group > 0:
            dst = self.target.cshape.center.x - self.master.cshape.center.x
            d = dst/abs(dst) if abs(dst) != 0 else 0
            dst = abs(dst)
            #print dst
            if d != self.master.direction:
                self.master.push_inst_task(Turn(self.master))
            if dst <= self.brain.eff_dst:
                self.master.push_inst_task(Close_Combat(self.master, self.brain, self.target))
            else:
                self.master.walk(self.master.direction)
                if self.master.wall & (con.LEFT | con.RIGHT):
                    self.master.push_inst_task(Jump(self.master))
        else:
            self.master.push_task(Stand(self.master, 1))
            self.brain.observed_units.remove(self.target)
            #print "OLOLO"
            return COMPLETE


class Close_Combat(Task):

    def __init__(self, master, brain, target):
        Task.__init__(self, master)
        self.brain = brain
        self.target = target

    def __call__(self, dt):
        #print "ololo"
        dst = abs(self.target.cshape.center.x - self.master.cshape.center.x)
        if dst <= self.brain.eff_dst and self.target.fight_group > 0:
            d = dst/abs(dst) if abs(dst) != 0 else 0
            if d != self.master.direction:
                self.master.push_inst_task(Turn(self.master, 11))
            hand = self.master.choose_free_hand()
            self.master.push_inst_task(Random_Attack(self.master, hand, self.target))
            mv = rnd.random()
            if mv < 0.05:
                self.master.push_inst_task(Walk(self.master, 0.1))
            elif mv < 0.01:
                self.master.push_inst_task(MoveBack(self.master, 0.1))
        else:
            return COMPLETE


class Walk(Task):

    def __call__(self, dt):
        Animate(self.master, 'walk')
        self.master.walk(self.master.direction)
        if self.master.wall & (con.LEFT | con.RIGHT):
                    self.master.push_inst_task(Jump(self.master))
        return Task.__call__(self, dt)


class Jump(Task):

    def __call__(self, dt):
        print self
        Animate(self.master, 'jump')
        self.master.jump()
        return COMPLETE


class MoveBack(Task):

    def __call__(self, dt):
        Animate(self.master, 'walk')
        self.master.walk(-self.master.direction)
        return Task.__call__(self, dt)


class Parry(Task):

    def __init__(self, master,  weapon, target):
        Task.__init__(self, master)
        self.target = target
        self.weapon = weapon

    def __call__(self, dt):
        hit = self.target
        hand = self.weapon
        if self.target.fight_group < 0 or rnd.random() < consts['params']['primitive']['mastery'] or hand is None or \
                not hand.available:
            #print 13
            return COMPLETE
        print "\nparry", hit, "\n"
        h = hit.start.y
        dire = hit.start.x - self.master.position[0]
        dire = dire/abs(dire) if dire != 0 else 0
        v = cross_hit_trace(hit)
        x = self.master.position[0] + self.master.width*dire
        start = eu.Vector2(x, h)
        self.master.use_hand(hand, [start, con.CHOP], [start+v])
        return COMPLETE


class Random_Attack(Task):

    def __init__(self, master, weapon, target):
        Task.__init__(self, master)
        self.target = target
        self.weapon = weapon

    def __call__(self, dt):
        hand = self.weapon
        target = self.target
        if rnd.random() < 0.05 or hand is None or not hand.available:
            return COMPLETE
        dire = target.position[0] - self.master.position[0]
        dire = dire/abs(dire) if dire != 0 else 0
        h = rnd.randint(-self.master.height/2, self.master.height/2)
        h += self.master.position[1]
        x = self.master.position[0] + self.master.width*dire
        targ_x = target.position[0] + rnd.randint(-target.width/2, target.width/2)
        targ_y = target.position[1] + rnd.randint(-target.height/2, target.height/2)
        start = eu.Vector2(x, h)
        end = (targ_x, targ_y)
        self.master.use_hand(hand, [start, con.CHOP], [end])
        return COMPLETE


class Aim(Task):

    def __init__(self, master,  weapon, target):
        Task.__init__(self, master)
        self.weapon = weapon
        self.target = target

    def __call__(self, dt):
        vx = self.target.position[0] - self.master.position[0]
        vy = self.target.position[1] - self.master.position[1]
        #print "POSITION", self.target.position[0], self.target.position[1]
        dx = con.LEFT if vx < 0 else con.RIGHT
        dy = con.DOWN if vy < 0 else con.UP
        v = eu.Vector2(vx, vy)
        v = (v/abs(v))*consts['tile_size']
        pos = self.master.position
        #print "START", pos
        while not self.target.cshape.touches_point(pos[0], pos[1]):
            cell = self.environment.get_at_pixel(pos[0], pos[1])
            if cell.get('right') and dx is con.LEFT or cell.get('left') and dx is con.RIGHT or\
                            cell.get('top') and dy is con.DOWN or cell.get('bottom') and dy is con.UP:
                return COMPLETE
            pos += v
            #print pos
        #print self.master, self.weapon, v
        self.master.push_task(Shoot(self.master, self.weapon, self.target))
        return COMPLETE


class Shoot(Task):

    def __init__(self, master, weapon, target):
        Task.__init__(self, master)
        self.weapon = weapon
        self.target = target

    def __call__(self, dt):
        hand = self.weapon
        start = self.master.position
        end = self.target.position
        self.master.use_hand(hand, [start], [], [end, True])
        return COMPLETE


class Body_Part_Move_To(Task):

    def __init__(self, master, pos, slot):
        Task.__init__(self, master)
        self.pos = pos
        self.slot = slot

    def __call__(self, dt):
        for body_part in self.master.body_parts:
            if body_part.slot is self.slot:
                body_part.set_pos(self.pos)
                return COMPLETE


class Body_Part_Move_On(Task):

    def __init__(self, master, v, slot):
        Task.__init__(self, master)
        self.v = v
        self.slot = slot

    def __call__(self, dt):
        for body_part in self.master.body_parts:
            if body_part.slot is self.slot:
                body_part.set_pos(body_part.shape.pc + self.v)
                return COMPLETE


class Stand(Task):

    def __call__(self, dt):
        self.master.stand()
        return COMPLETE


class Turn(Task):

    def __call__(self, dt):
        self.master.turn()
        #self.master.direction = -self.master.direction
        return COMPLETE


class Controlling(Task):

    bind = con.bindings
    pressed = False

    def __init__(self, master):
        Task.__init__(self, master)
        loc = self.master.get_ancestor(layer.ScrollableLayer)
        self.key = loc.loc_key_handler
        self.mouse = loc.loc_mouse_handler
        self.scroller = loc.scroller
        self.static_objs = loc.static_collman
        self.triggers = loc.scripts
        #print self.scroller

    def __call__(self, dt):
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
                    self.master.walk(hor_dir)
                    Animate(self.master, 'walk')

            #Use items
            first_item_trigger = self.mouse[self.bind['first_hand']]
            alt = self.key[self.bind['alt_mode']]
            pos = self.mouse['pos']
            self.master.use_item(MAIN, first_item_trigger, [pos, alt])
            second_item_trigger = self.mouse[self.bind['second_hand']]
            self.master.use_item(SECONDARY, second_item_trigger, [pos, alt])

        action = self.key[self.bind['action']]
        if action:
            #print "CONTROLLER", self.key
            self.key[self.bind['action']] = False
            triggers = filter(lambda sc: 'trigger' in sc.properties,
                              self.triggers.iter_colliding(self.master))
            #print list(triggers)
            for tr in triggers:
                self.master.activate_trigger(tr)
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


class Task_Manager(object):

    def __init__(self):
        self.tasks = deque()

    def cur_task(self):
        if self.tasks:
            return self.tasks[0]
        else:
            return None

    def push_task(self, task):
        old_task = self.tasks.popleft() if not self.is_empty() else None
        self.tasks.appendleft(task)
        if old_task:
            self.tasks.appendleft(old_task)
        #self.tasks.append(Pause(None, TASK_CHANGE_TIME))

    def push_instant_task(self, task):
        #self.tasks.appendleft(Pause(None, TASK_CHANGE_TIME))
        self.tasks.appendleft(task)

    def pop_task(self):
        return self.tasks.popleft()

    def clear_queue(self):
        self.tasks = deque()

    def num_of_tasks(self):
        return len(self.tasks)

    def is_empty(self):
        return self.num_of_tasks() <= 0


class Brain(ac.Action):
    
    master = property(lambda self: self.target)
    #recovery = property(lambda self: self.master.recovery, _set_rec)
    fight_group = -1
    
    def start(self):
        self.master.fight_group = self.fight_group
        self.environment = self.master.tilemap
        self.task_manager = Task_Manager()
        #self.tilemap = self.master.get_ancestor(cocos.layer.ScrollableLayer).force_ground

    def step(self, dt):
        self.master.update(dt)
        self.sensing()
        self.activity(dt)
        
    def sensing(self):
        pass
    
    def activity(self, dt):
        #print self.task_manager.tasks
        if not self.task_manager.is_empty() and self.task_manager.cur_task()(dt) is COMPLETE:
            self.task_manager.pop_task()


class Controller(Brain):
    
    bind = con.bindings
    fight_group = consts['group']['hero']
    
    def start(self):
        Brain.start(self)
        self.task_manager.push_task(Controlling(self.master))


class Enemy_Brain(Brain):

    fight_group = consts['group']['opponent']


class Dummy(Enemy_Brain):

    range_of_vision = con.primitive['range_of_vision']

    def start(self):
        Brain.start(self)
        self.vision = self.master.get_ancestor(layer.ScrollableLayer).collman
        self.visible_actors_wd = []
        self.visible_hits_wd = []
        self.task_manager.push_task(Task(self, 1))

        self.state = 'stand'
    
    #def activity(self, dt):
    #    self.master.sit()
    #    pass
    #    hand = self.master.choose_free_hand()
        #if hand is not None:
        #    start = self.master.position - eu.Vector2(self.master.width, 0.0)
        #    target = self.master.position + eu.Vector2(-50.0, 50.0)
        #    self.master.use_hand(hand, [start, con.CHOP], [target])

    def sensing(self):
        self.clear_vision()
        for obj_wd in self.vision.objs_near_wdistance(self.master, self.range_of_vision):
            if obj_wd[0].fight_group < consts['slash_fight_group']:
                self.visible_actors_wd.append(obj_wd)
            elif obj_wd[0].fight_group < consts['missile_fight_group']:
                self.visible_hits_wd.append(obj_wd)
            else:
                pass
        for hit_wd in self.visible_hits_wd:
            hit, dst = hit_wd
            if self.is_enemy(hit):
                if self.master.cshape.overlaps(hit.cshape):
                    hand = self.master.choose_free_hand()
                    self.task_manager.push_instant_task(Parry(self.master, hand, hit))
                    #print self.task_manager.tasks
                break

    def is_enemy(self, other):
        if other.fight_group < 100:
            return self.master.fight_group is not other.fight_group
        else:
            return self.master.fight_group is not other.base_fight_group

    def clear_vision(self):
        self.visible_actors_wd = []
        self.visible_hits_wd = []


class Primitive_AI(Enemy_Brain):

    mastery = con.primitive['mastery']
    range_of_vision = con.primitive['range_of_vision']
    closest = con.primitive['closest']
    
    def start(self):
        Brain.start(self)
        self.vision = self.master.get_ancestor(layer.ScrollableLayer).collman
        self.visible_actors = []
        self.visible_hits = []
        self.observed_units = set()

        self.state = 'stand'
        
    def sensing(self):
        self.clear_vision()
        for obj in self.vision.objs_near(self.master, self.range_of_vision):
            if obj.fight_group < consts['slash_fight_group']:
                self.visible_actors.append(obj)
            elif obj.fight_group < consts['missile_fight_group']:
                self.visible_hits.append(obj)
            else:
                pass
        #print self.visible_actors_wd
        for enemy in filter(lambda x: self.is_enemy(x), self.visible_actors):
            if enemy not in self.observed_units:
                print 123, enemy
                self.task_manager.push_task(Approaches(self.master, self, enemy))
                self.observed_units.add(enemy)
        for hit in self.visible_hits:
            if self.is_enemy(hit):
                if self.master.cshape.overlaps(hit.cshape):
                    hand = self.master.choose_free_hand()
                    self.task_manager.push_instant_task(Parry(self.master, hand, hit))
                break

    def clear_vision(self):
        self.visible_actors = []
        self.visible_hits = []

    def is_enemy(self, other):
        if other.fight_group >= 0:
            if other.fight_group < 100:
                return self.master.fight_group is not other.fight_group
            else:
                return self.master.fight_group is not other.base_fight_group

    def is_in_touch(self, other):
        return self.master.cshape.overlaps(other.cshape)


class Base_Enemy_Mind(Primitive_AI):

    def start(self):
        # Primitive_AI.start(self)
        # self.eff_dst = self.master.hands[0].length * consts['effective_dst']
        pass
        #self.task_manager.push_task()


if __name__ == "__main__":
    print "Hello World"
