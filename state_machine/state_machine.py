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
Некоторые переходы нельзя отменять.
"""
__author__ = 'ecialo'
from collections import defaultdict
from transitions_table import Transitions_Table
from registry.utility import binary_list
STAND, WALK, CROUCH, RUN, FALL, JUMP = binary_list(6)
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


IDLE = binary_list(1)


def lockable(command):

    def lockable_command(self, *args, **kwargs):
        if self.is_locked:
            return self.state_id
        else:
            return command(self, *args, **kwargs)

    return lockable_command


# def lock(command):
#
#     def llock(self, *args, **kwargs):
#         command(self, *args, **kwargs)
#         self.is_locked = True
#
#     return llock
# 1) Движение
# 2) Приседание
# 3) Прыжок

EPS = 1.0

transitions = Transitions_Table('state_machine/animation_table')


class Cool_State(object):

    state_id = None

    def __init__(self, actor):

        self.actor = actor
        self.body = actor.body
        self.b2body = actor.b2body
        self.characteristics = actor.body.characteristics
        self._animation = None
        self.animations = {}
        self.animation = self.state_id

        self.time = 0.0
        self.loop = True
        self.is_locked = False
        self.is_on_change = False
        self.target_state_id = self.state_id

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self, state_id):
        pair = (self.state_id, state_id)
        try:
            self._animation = self.animations[pair]
        except KeyError:
            self.animations[pair] = transitions.get_animation(self.body, *pair)
            self._animation = self.animations[pair]

    def update(self, dt):
        self.time += dt
        if self.animation:
            self.animation.apply(time=self.time,
                                 skeleton=self.body,
                                 loop=self.loop)
        self.body.skeleton_data.update_transform()
        if self.is_on_change and self.time >= self.animation.duration:
            # self.time = 0.0
            # self.is_locked = False
            return self.target_state_id
        else:
            return self.state_id

    def move(self, direction):
        pass

    def crouch(self, is_crouch):
        pass

    def jump(self):
        pass

    def setup_transition(self, transition_id):
        if transition_id is not self.target_state_id:
            self.target_state_id = transition_id
            self.is_on_change = transition_id is not self.state_id
            self.loop = not self.is_on_change
            self.animation = transition_id
            self.time = 0.0


class Cool_Stand(Cool_State):

    state_id = STAND

    @lockable
    def move(self, direction):
        self.actor.body.move(direction)
        if direction:
            if direction != self.actor.direction:
                self.actor.direction *= COUNTER_DIRECTION
        if abs(self.actor.b2body.linearVelocity[0]) > EPS:
            self.setup_transition(WALK)

    def crouch(self, is_crouch):
        if is_crouch:
            self.setup_transition(CROUCH)
            self.is_locked = True

    def jump(self):
        self.actor.body.jump()
        self.setup_transition(FALL)


class Cool_Crouch(Cool_State):

    state_id = CROUCH

    def crouch(self, is_crouch):
        if not is_crouch:
            self.setup_transition(STAND)
            self.is_locked = True

    @lockable
    def move(self, direction):
        self.actor.body.move(direction)
        if abs(self.actor.b2body.linearVelocity[0]) > EPS:
            self.setup_transition(CROUCH | WALK)


class Cool_Walk(Cool_State):

    state_id = WALK

    def move(self, direction):
        self.actor.body.move(direction)
        if abs(self.actor.b2body.linearVelocity[0]) > self.characteristics.max_speed/3:
            self.setup_transition(RUN)
        elif abs(self.actor.b2body.linearVelocity[0]) <= EPS:
            self.setup_transition(STAND)

    def jump(self):
        self.setup_transition(FALL)


class Cool_Run(Cool_State):

    state_id = RUN

    def move(self, direction):
        self.actor.body.move(direction)
        if abs(self.actor.b2body.linearVelocity[0]) <= self.characteristics.max_speed/3:
            self.setup_transition(WALK)

    def crouch(self, is_crouch):
        if is_crouch:
            self.setup_transition(CROUCH | RUN)
            self.is_locked = True

    def jump(self):
        self.setup_transition(FALL)


class Cool_Slide(Cool_State):

    state_id = CROUCH | RUN

    def move(self, direction):
        if abs(self.actor.b2body.linearVelocity[0]) <= EPS:
            self.setup_transition(CROUCH)


class Cool_Crawl(Cool_State):

    state_id = CROUCH | WALK

    def move(self, direction):
        self.actor.body.move(direction)
        if direction:
            if direction != self.actor.direction:
                self.actor.direction *= COUNTER_DIRECTION
        if abs(self.actor.b2body.linearVelocity[0]) <= EPS:
            self.setup_transition(CROUCH)


class Cool_Fall(Cool_State):

    state_id = FALL

    def move(self, direction):
        self.actor.body.move(direction, 0.2)    # Незначительно корректировать полёт
        if self.actor.on_ground:
            self.setup_transition(STAND)

    def jump(self):
        self.actor.body.jump()


class Cool_Jump(Cool_State):

    state_id = JUMP

    def move(self, direction):
        #TODO заменить константу на что-то более умное
        self.actor.body.move(direction, 0.2)    # Незначительно корректировать полёт

    def jump(self):
        pass    #Тянуть вверх с силой обратно пропорциональной времени


class Cool_State_Machine(object):

    def __init__(self, actor):
        self.states = {STAND: Cool_Stand(actor),
                       WALK: Cool_Walk(actor),
                       CROUCH: Cool_Crouch(actor),
                       RUN: Cool_Run(actor),
                       CROUCH | WALK: Cool_Crawl(actor),
                       FALL: Cool_Fall(actor),
                       CROUCH | RUN: Cool_Slide(actor)}
        self._current_state = None
        self.current_state = self.states[STAND]

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        if state is not self._current_state:
            self._current_state = state
            state.setup_transition(state.state_id)
            state.is_locked = False

    def move(self, direction):
        self.current_state.move(direction)

    def crouch(self, is_crouch):
        self.current_state.crouch(is_crouch)

    def jump(self):
        self.current_state.jump()

    def update(self, dt):
        self.current_state = self.states[self.current_state.update(dt)]


if __name__ == '__main__':
    print transitions