# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "Ecialo"

import random as rnd

from cocos import actions as ac
from cocos import euclid as eu
from cocos import layer
import heapq as q

import consts as con

consts = con.consts

COMPLETE = True


def cross_hit_trace(self, hit):
    v = hit.trace.v
    nv = v.cross()
    if v.x >= 0 and v.y < 0 or v.x < 0 and v.y < 0:
        return nv
    else:
        return -nv


def _set_rec(self, value):
    self.master.recovery = value


class Task(object):

    hands = property(lambda self: self.master.hands)

    def __init__(self, master, priority, time=None):
        self.priority = priority
        self.master = master
        self.time = time

    def __cmp__(self, other):
        return other.priority - self.priority

    def __call__(self, dt):
        if self.time is not None:
            self.time -= dt
            return COMPLETE if self.time <= 0.0 else None


class Walk(Task):

    def __call__(self, dt):
        self.master.walk(self.master.direction)
        if self.master.wall & (con.LEFT | con.RIGHT):
                    self.master.push_task(Jump(self.master, 98))
        return Task.__call__(self, dt)


class Jump(Task):

    def __call__(self, dt):
        self.master.jump()
        return COMPLETE


class Dance_Around(Task):

    def __init__(self, master, target, priority):
        Task.__init__(self, master, priority)
        self.target = target

    def __call__(self, dt):
        mv = rnd.random()
        print mv
        if mv < 0.05:
            self.prev_move = dir
            self.master.push_task(Walk(self.master, self.priority + 1, 0.1))
        elif mv < 0.01:
            self.prev_move = -dir
            self.mt = 0.5
            self.master.push_task(MoveBack(self.master, self.priority + 1, 0.1))
        else:
            pass
        return Task.__call__(self, dt)


class MoveBack(Task):

    def __call__(self, dt):
        self.master.walk(-self.master.direction)
        return Task.__call__(self, dt)


class Parry(Task):

    def __init__(self, master, priority, target):
        Task.__init__(self, master, priority)
        self.target = target

    def __call__(self, dt):
        hit = self.target
        hand = self.master.choose_free_hand()
        if rnd.random() < self.mastery or hand is None:
            #print 13
            return COMPLETE
        #print "parry"
        h = hit.start.y
        dire = hit.start.x - self.master.position[0]
        dire = dire/abs(dire) if dire != 0 else 0
        v = cross_hit_trace(hit)
        x = self.master.position[0] + self.master.width*dire
        start = eu.Vector2(x, h)
        self.master.use_hand(hand, [start, con.CHOP], [start+v])
        return COMPLETE


class Random_Attack(Task):

    def __init__(self, master, priority, target):
        Task.__init__(self, master, priority)
        self.target = target

    def __call__(self, dt):
        hand = self.master.choose_free_hand()
        target = self.target
        if rnd.random() < 0.05 or hand is None:
            return COMPLETE
        dire = target.position[0] - self.master.position[0]
        dire = dire/abs(dire) if dire != 0 else 0
        h = rnd.randint(-self.master.height/2, self.master.height/2)
        h += self.master.position[1]
        x = self.master.position[0] + self.master.width*dire
        targ_x = target.position[0] + rnd.randint(-target.width/2, -target.width/2)
        targ_y = target.position[1] + rnd.randint(-target.height/2, -target.height/2)
        start = eu.Vector2(x, h)
        end = (targ_x, targ_y)
        self.master.use_hand(hand, [start, con.CHOP], [end])
        return COMPLETE


class Stand(Task):

    def __call__(self, dt):
        self.master.stand()
        return COMPLETE


class Turn(Task):

    def __call__(self, dt):
        self.master.direction = -self.master.direction
        return COMPLETE


class Controlling(Task):

    bind = consts['bindings']
    pressed = False

    def __init__(self, master, priority):
        Task.__init__(self, master, priority)
        self.key = self.master.get_ancestor(layer.ScrollableLayer).loc_key_handler
        self.mouse = self.master.get_ancestor(layer.ScrollableLayer).loc_mouse_handler
        self.scroller = self.master.get_ancestor(layer.ScrollableLayer).scroller
        self.static_objs = self.master.get_ancestor(layer.ScrollableLayer).static_collman

    def __call__(self, dt):
        if self.key[self.bind['down']]:
            self.master.sit()
        else:
            hor_dir = self.key[self.bind['right']] - self.key[self.bind['left']]
            if self.key[self.bind['jump']] and self.master.on_ground:
                self.master.jump()
            if hor_dir == 0:
                self.master.stand()
            else:
                self.master.walk(hor_dir)

        #Action
        items = len(self.hands)
        first_hand_ac = self.mouse[self.bind['first_hand']]
        alt = self.key[self.bind['alt_mode']]
        pos = self.mouse['pos']
        first_item = self.hands[con.FIRST_HAND]

        if first_hand_ac and not first_item.on_use:
            first_item.start_use(pos, con.STAB if alt else con.CHOP)
        elif first_hand_ac and first_item.on_use and first_item.available:
            first_item.continue_use(pos)
        elif not first_hand_ac and first_item.on_use and first_item.available:
            first_item.end_use(pos)
        else:
            pass

        if items > 1:
            second_hand_ac = self.mouse[self.bind['second_hand']]
            second_item = self.hands[con.SECOND_HAND]
            if second_hand_ac and not second_item.on_use:
                second_item.start_use(pos, con.STAB if alt else con.CHOP)
            elif second_hand_ac and second_item.on_use and second_item.available:
                second_item.continue_use(pos)
            elif not second_hand_ac and second_item.on_use and second_item.available:
                second_item.end_use(pos)
            else:
                pass

        gain = self.key[self.bind['gain']]
        if gain:
            items = self.static_objs.objs_touching_point(*pos)
            for item in items:
                self.master.put_item(item)
                item.get_up()

        inv = self.key[self.bind['inventory']]
        if inv and not self.pressed:
            self.master.open()
            self.pressed = True
        elif inv and self.pressed:
            self.master.close()
            self.pressed = False
        else:
            pass
        #cx, cy = self.master.position
        #print cx, cy
        self.scroller.set_focus(*self.master.position)


class Task_Manager(object):

    def __init__(self):
        self.tasks = []

    def cur_task(self):
        return self.tasks[0]

    def push_task(self, task):
        q.heappush(self.tasks, task)

    def pop_task(self):
        return q.heappop(self.tasks)

    def clear_queue(self):
        self.tasks = []

    def num_of_tasks(self):
        return len(self.tasks)


class Brain(ac.Action):
    
    master = property(lambda self: self.target)
    #recovery = property(lambda self: self.master.recovery, _set_rec)
    fight_group = -1
    
    def start(self):
        self.master.fight_group = self.fight_group
        self.task_manager = Task_Manager()
        #self.tilemap = self.master.get_ancestor(cocos.layer.ScrollableLayer).force_ground
    
    def step(self, dt):
        self.master.update(dt)
        self.sensing()
        self.activity(dt)
        
    def sensing(self):
        pass
    
    def activity(self, dt):
        if self.task_manager.cur_task()(dt) is COMPLETE:
            self.task_manager.pop_task()


class Controller(Brain):
    
    bind = consts['bindings']
    fight_group = consts['group']['hero']
    
    def start(self):
        Brain.start(self)
        self.task_manager.push_task(Controlling(self.master, 1))


class Enemy_Brain(Brain):

    fight_group = consts['group']['opponent']


class Dummy(Enemy_Brain):
    
    def activity(self, dt):
        self.master.sit()
        pass
        #hand = self.choose_free_hand()
        #if hand is not None:
        #    start = self.master.position - eu.Vector2(self.master.width, 0.0)
        #    target = self.master.position + eu.Vector2(-50.0, 50.0)
        #    self.use_hand(hand, [start, con.CHOP], [target])


class Primitive_AI(Enemy_Brain):

    mastery = consts['params']['primitive']['mastery']
    range_of_vision = consts['params']['primitive']['range_of_vision']
    closest = consts['params']['primitive']['closest']
    
    def start(self):
        Brain.start(self)
        self.vision = self.master.get_ancestor(layer.ScrollableLayer).collman
        self.visible_actors_wd = []
        self.visible_hits_wd = []

        self.prev_move = 0
        self.state = 'stand'
        self.eff_dst = self.master.hands[0].length * consts['effective_dst']
        
    def sensing(self):
        self.clear_vision()
        for obj_wd in self.vision.objs_near_wdistance(self.master, self.range_of_vision):
            if obj_wd[0].fight_group < consts['slash_fight_group']:
                self.visible_actors_wd.append(obj_wd)
            elif obj_wd[0].fight_group < consts['missile_fight_group']:
                self.visible_hits_wd.append(obj_wd)
            else:
                pass
        #print self.visible_actors_wd
        for unit_wd in self.visible_actors_wd:
            unit, dst = unit_wd
            if self.is_enemy(unit):
                d = unit.cshape.center.x - self.master.cshape.center.x
                d = d/abs(d) if d != 0 else 0
                if d != self.master.direction:
                    self.task_manager.push_task(Turn(self.master, 98))
                if self.state is 'stand':
                    self.state = 'approach'
                    self.task_manager.push_task(Walk(self.master, 1))
                elif self.state is 'approach':
                    if dst <= self.eff_dst:
                        self.state = 'eff'
                        self.task_manager.push_task(Dance_Around(self.master, unit, 2))
                elif self.state is 'eff':
                    #print self.task_manager.cur_task(), self.task_manager.tasks
                    self.task_manager.push_task(Random_Attack(self.master, 97, unit))

                break
        else:
            self.task_manager.clear_queue()
            self.state = 'stand'
            self.task_manager.push_task(Stand(self.master, 1))
        for hit_wd in self.visible_hits_wd:
            hit, dst = hit_wd
            if self.is_enemy(hit):
                if self.master.cshape.overlaps(hit):
                    self.task_manager.push_task(Parry(self.master, 99, hit))
                break

    def clear_vision(self):
        self.visible_actors_wd = []
        self.visible_hits_wd = []

    def is_enemy(self, other):
        if other.fight_group < 100:
            return self.master.fight_group is not other.fight_group
        else:
            return self.master.fight_group is not other.base_fight_group

    def is_in_touch(self, other):
        return self.master.cshape.overlaps(other.cshape)

if __name__ == "__main__":
    print "Hello World"
