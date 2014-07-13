# -*- coding: utf-8 -*-
"""
Что эта хрень должна уметь:
1) Применять анимацию+действие по ключу.
2) В зависимости от состояний актёра менять анимацию от вызовов(большая скорость - бег, маленькая - ходьба)
3) Переключать состояния
4) Работать с зацикленными и не очень анимациями
5) Пущать обратную анимацию в обратных переходах



Переходы могут быть просто анимацией, плавным переходом и обратной анимацией
Если во время перехода отменить действие, то всё вернётся к состоянию из которого был переход
"""
__author__ = 'ecialo'
from registry.utility import binary_list
STAND, WALK, CROUCH, RUN, FALL = binary_list(5)
UNCHANGED = 0
COUNTER_DIRECTION = -1


def unbreakeable_transition(command):

    def unbreakable(*args, **kwargs):
        self = args[0]
        if self._transition is not None:
            return CROUCH
        else:
            return command(*args, **kwargs)
    unbreakable.__name__ = command.__name__
    return unbreakable


class State(object):

    name = None

    def __init__(self, actor):
        self.actor = actor
        self.body = actor.body
        self.characteristics = actor.body.characteristics
        self.b2body = actor.b2body

        self.animation = None
        self.to_state = None
        self.time = 0.0
        self.loop = False

    def setup_transition(self, transition, state_id):
        self.time = 0.0
        self.animation = transition
        self.to_state = state_id
        self.loop = state_id is self.name

    def is_complete_transition(self):
        trs = self.animation
        # if trs:
        #     print trs.duration, self.time
        if trs and self.time >= trs.duration:
            return True
        else:
            return False

    def move(self, direction):
        return UNCHANGED

    def crouch(self):
        return UNCHANGED

    def jump(self):
        return UNCHANGED

    def take_hit(self):
        return UNCHANGED

    def update(self, dt):
        self.time += dt
        if self.animation:
            self.animation.apply(time=self.time,
                                 skeleton=self.body,
                                 loop=self.loop)
        self.body.skeleton_data.update_transform()


class Stand(State):

    name = STAND

    def move(self, direction):
        if direction:
            self.actor.b2body.ApplyForceToCenter((self.characteristics.acceleration*direction, 0), 1)
            if self.actor.direction != direction:
                self.actor.direction *= COUNTER_DIRECTION
            return WALK
        return STAND

    def crouch(self):
        return CROUCH

    def jump(self):
        return FALL


class Walk(State):

    name = WALK

    def move(self, direction):
        self.actor.b2body.ApplyForceToCenter((self.characteristics.acceleration*direction, 0), 1)
        #print self.actor.direction, direction
        if abs(self.actor.b2body.linearVelocity[0]) >= self.characteristics.max_speed/2:
            return RUN
        elif direction != self.actor.direction: # and abs(self.actor.b2body.linearVelocity[0]) < self.characteristics.max_speed/8:
            return STAND
        return WALK

    # def update(self, dt):
    #     if abs(self.actor.b2body.linearVelocity[0]) > self.characteristics.max_speed:
    #         self.actor.b2body.linearVelocity[0] = self.characteristics.max_speed * self.actor.direction
    #     super(Walk, self).update(dt)


class Crouch(Stand):

    name = CROUCH | STAND

    def move(self, direction):
        if direction:
            self.actor.b2body.ApplyForceToCenter((self.characteristics.acceleration*direction, 0), 1)
            if self.actor.direction != direction:
                self.actor.direction *= COUNTER_DIRECTION
            return WALK | CROUCH
        return STAND

    def crouch(self):
        return CROUCH


class Crawling(State):

    name = CROUCH | WALK

    def move(self, direction):
        self.actor.b2body.ApplyForceToCenter((self.characteristics.acceleration*direction, 0), 1)
        if direction != self.actor.direction or abs(self.actor.b2body.linearVelocity[0]) < self.characteristics.max_speed/3:
            return CROUCH | STAND
        return CROUCH | WALK

    def update(self, dt):
        if abs(self.actor.b2body.linearVelocity[0]) > self.characteristics.max_speed/3:
            self.actor.b2body.linearVelocity[0] = self.characteristics.max_speed/3 * self.actor.direction
        super(Crawling, self).update(dt)


class Running(State):

    name = RUN

    def move(self, direction):
        self.actor.b2body.ApplyForceToCenter((self.characteristics.acceleration*direction, 0), 1)
        if abs(self.actor.b2body.linearVelocity[0]) < self.characteristics.max_speed/2:
            return WALK
        else:
            return RUN

    def update(self, dt):
        if abs(self.actor.b2body.linearVelocity[0]) > self.characteristics.max_speed:
            self.actor.b2body.linearVelocity[0] = self.characteristics.max_speed * self.actor.direction
        super(Running, self).update(dt)


class Fall(State):

    def move(self, direction):
        return FALL


class Reversed_Animation(object):

    def __init__(self, animation):
        self.animation = animation
        self.duration = animation.duration

    def apply(self, time=0.0, skeleton=None, loop=False):
        self.animation.apply(time=self.duration-time, skeleton=skeleton, loop=loop)


class Smooth_Animation(object):

    def __init__(self, from_anim, to_anim):
        # print from_state, to_state
        # to_anim = to_state.animation
        # from_anim = from_state.animation
        print from_anim, to_anim
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
                       RUN: Running(actor),
                       CROUCH | STAND: Crouch(actor),
                       CROUCH | WALK: Crawling(actor),
                       FALL: Fall(actor)}

        self.transitions = {}
        transitions = {(STAND, STAND): None,
                       (STAND, WALK): None,
                       (WALK, STAND): 'stop',
                       (WALK, WALK): 'walking',
                       (STAND, STAND | CROUCH): 'Bow',
                       (STAND, WALK | CROUCH): 'Bow',
                       (STAND | CROUCH, STAND): None,
                       (STAND | CROUCH, STAND | CROUCH): None,
                       (STAND | CROUCH, CROUCH | WALK): None,
                       (CROUCH | WALK, STAND | CROUCH): None,
                       (CROUCH | WALK, CROUCH | WALK): 'crawl',
                       (WALK, RUN): None,
                       (RUN, WALK): None,
                       (RUN, RUN): 'run',
                       (FALL, FALL): 'fall',
                       (STAND, FALL): 'jump',
                       (WALK, FALL): 'long_jump',
                       (RUN, FALL): 'long_jump',
                       (FALL, STAND): 'Bow'}
        pre_trans = {}
        for trs, aniname in transitions.iteritems():
            try:
                pre_trans[trs] = actor.body.find_animation(aniname)
            except KeyError:
                pre_trans[trs] = None
        for trs, aniname in pre_trans.iteritems():
            if pre_trans[trs]:
                self.transitions[trs] = pre_trans[trs]
            elif pre_trans[(trs[1], trs[0])]:
                self.transitions[trs] = Reversed_Animation(pre_trans[(trs[1], trs[0])])
            else:
                try:
                    #print trs
                    self.transitions[trs] = Smooth_Animation(pre_trans[(trs[0], trs[0])],
                                                             pre_trans[(trs[1], trs[1])])
                except KeyError as err:
                    print err
                    self.transitions[trs] = None

        #print self.transitions

        self.state = self.states[STAND]
        self.next_state_index = STAND
        self.current_state_index = STAND
        self.state.setup_transition(transitions[(STAND, STAND)], STAND)

    def update(self, dt):
        print self.state
        self.state.update(dt)
        #print self.state, self.state.to_state, self.next_state_index, self.state.animation
        #print "STATE", self.current_state_index, "NEXT", self.next_state_index
        # Если состояние полностью перешлось -> сменить его
        if self.state.is_complete_transition():
            self.current_state_index = self.state.to_state
            self.state = self.states[self.current_state_index]
            self.state.setup_transition(self.transitions[self.current_state_index, self.current_state_index],
                                        self.current_state_index)
        # Если состояние не полностью перешлось,
        # или не переходилось вовсе а мы уже делаем что-то другое - сбросить переход и делать это
        elif self.next_state_index != self.state.to_state:
            self.state.setup_transition(self.transitions[(self.current_state_index, self.next_state_index)],
                                        self.next_state_index)
        else:
            pass
        # Иначе делать то что делактся
        self.next_state_index = UNCHANGED

    def move(self, direction):
        self.next_state_index |= self.state.move(direction)

    def jump(self):
        if self.state.jump():
            self.next_state_index = FALL

    def crouch(self):
        self.next_state_index |= self.state.crouch()

    def take_hit(self):
        self.state.take_hit()