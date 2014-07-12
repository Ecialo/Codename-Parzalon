# -*- coding: utf-8 -*-
"""
Что эта хрень должна уметь:
1) Применять анимацию+действие по ключу.
2) В зависимости от состояний актёра менять анимацию от вызовов(большая скорость - бег, маленькая - ходьба)
3) Переключать состояния
4) Работать с зацикленными и не очень анимациями
5) Пущать обратную анимацию в обратных переходах


Переходы могут быть просто анимацией, плавным переходом и обратной анимацией
"""
__author__ = 'ecialo'
from registry.utility import binary_list
STAND, WALK, CROUCH = binary_list(3)
UNCHANGED = 0
COUNTER_DIRECTION = -1


class State(object):

    name = None

    def __init__(self, actor):
        self.actor = actor
        self.body = actor.body
        self.characteristics = actor.body.characteristics
        self.b2body = actor.b2body
        self._transition = None
        try:
            self.animation = self.body.find_animation(self.name)
        except KeyError:
            self.animation = None
        self.time = 0.0

    def move(self, direction):
        return UNCHANGED

    def crouch(self):
        return UNCHANGED

    def jump(self):
        return UNCHANGED

    def take_hit(self):
        return UNCHANGED

    def update(self, dt):
        if self._transition:
            self.transition(dt)
        elif self.animation:
            self.idle(dt)
        self.body.skeleton_data.update_transform()

    def idle(self, dt):
        self.time += dt
        self.animation.apply(time=self.time,
                             skeleton=self.body,
                             loop=True)

    def transition(self, dt):
        self.time += dt
        self._transition.apply(time=self.time,
                               skeleton=self.body,
                               loop=False)
        if self.time >= self._transition.duration:
            self._transition = None


class Stand(State):

    name = None

    def move(self, direction):
        if direction:
            if self.actor.direction != direction:
                self.actor.direction *= COUNTER_DIRECTION
            return WALK
        return STAND

    def crouch(self):
        return CROUCH


class Walk(State):

    name = 'walking'

    def move(self, direction):
        self.actor.b2body.ApplyForceToCenter((self.characteristics.acceleration*direction, 0), 1)
        #print self.actor.direction, direction
        if self.actor.direction != direction:
            return STAND
        return WALK

    def update(self, dt):
        if abs(self.actor.b2body.linearVelocity[0]) > self.characteristics.max_speed:
            self.actor.b2body.linearVelocity[0] = self.characteristics.max_speed * self.actor.direction
        super(Walk, self).update(dt)


class Crouch(Stand):
    pass


class Crawling(Walk):

    name = 'crawl'

    def move(self, direction):
        return CROUCH | super(Crawling, self).move(direction)


class Reversed_Animation(object):

    def __init__(self, animation):
        self.animation = animation
        self.duration = animation.duration

    def apply(self, time=0.0, skeleton=None, loop=False):
        self.animation.apply(time=self.duration-time, skeleton=skeleton, loop=loop)


class Smooth_Animation(object):

    def __init__(self, from_state, to_state):
        print from_state, to_state
        to_anim = to_state.animation
        from_anim = from_state.animation
        if to_anim is None:
            raise KeyError      # TODO Заменить на свой тип ошибок
        self.to_animation = to_anim
        self.from_animation = from_anim
        if from_anim:
            self.duration = min(to_anim.duration, from_anim.duration)
        else:
            self.duration = to_anim.duration

    def apply(self, time=0.0, loop=False, skeleton=None):
        part = time/self.duration
        self.to_animation.mix(time, skeleton, loop, part)
        if self.from_animation:
            self.from_animation.mix(time, skeleton, loop, 1 - part)




class State_Machine(object):

    def __init__(self, actor):
        self.states = {STAND: Stand(actor),
                       WALK: Walk(actor),
                       CROUCH | STAND: Crouch(actor),
                       CROUCH | WALK: Crawling(actor)}

        self.transitions = {}
        transitions = {(STAND, WALK): 'None',
                       (WALK, STAND): 'stop',
                       (STAND, STAND | CROUCH): 'Bow',
                       (STAND | CROUCH, STAND): 'None',
                       (STAND | CROUCH, CROUCH | WALK): 'None',
                       (CROUCH | WALK, STAND | CROUCH): 'None'}
        pre_trans = {}
        for trs, aniname in transitions.iteritems():
            try:
                pre_trans[trs] = actor.body.find_animation(aniname)
            except KeyError:
                pre_trans[trs] = transitions[trs]
        for trs, aniname in pre_trans.iteritems():
            if type(pre_trans[trs]) is not str:
                self.transitions[trs] = pre_trans[trs]
            elif type(pre_trans[trs]) is str and type(pre_trans[(trs[1], trs[0])]) is not str:
                self.transitions[trs] = Reversed_Animation(pre_trans[(trs[1], trs[0])])
            else:
                try:
                    self.transitions[trs] = Smooth_Animation(self.states[trs[0]], self.states[trs[1]])
                except KeyError:
                    self.transitions[trs] = None

        #print self.transitions

        self.state = self.states[STAND]
        self.next_state_index = STAND
        self.current_state_index = STAND

    def update(self, dt):
        #print self.state
        self.state.update(dt)
        #print "STATE", self.current_state_index, "NEXT", self.next_state_index
        if self.next_state_index is not self.current_state_index:
            trs = (self.current_state_index, self.next_state_index)
            self.state.time = 0.0
            self.state = self.states[self.next_state_index]
            print self.transitions[trs], trs
            self.state._transition = self.transitions[trs]  # НУ Ё!
            self.current_state_index = self.next_state_index
        self.next_state_index = STAND

    def move(self, direction):
        self.next_state_index ^= STAND ^ self.state.move(direction)

    def jump(self):
        self.state.jump()

    def crouch(self):
        self.next_state_index |= self.state.crouch()

    def take_hit(self):
        self.state.take_hit()