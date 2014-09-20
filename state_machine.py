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
        if direction != self.actor.direction:
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
        self.duration = 0

    def apply(self, time=0.0, loop=False, skeleton=None):
        pass
        # part = time/self.duration
        # self.to_animation.mix(time, skeleton, loop, 1)
        # if self.from_animation:
        #     self.from_animation.mix(time, skeleton, loop, part)


class Instant_Animation(Smooth_Animation):
    pass


class State_Machine(object):

    def __init__(self, actor):
        self.states = {STAND: Stand(actor),
                       WALK: Walk(actor),
                       RUN: Running(actor),
                       CROUCH | STAND: Crouch(actor),
                       CROUCH | WALK: Crawling(actor),
                       FALL: Fall(actor)}

        self.transitions = {}
        transitions = {(STAND, STAND): 'stop_cycle',
                       (STAND, WALK): None,
                       (WALK, STAND): 'stop',
                       (WALK, WALK): 'walking',
                       (STAND, STAND | CROUCH): None,
                       (STAND, WALK | CROUCH): 'Bow',
                       (STAND | CROUCH, STAND): None,
                       (STAND | CROUCH, STAND | CROUCH): 'Bow_cycle',
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
                print aniname
                pre_trans[trs] = actor.body.find_animation(aniname)
                print "Sucses"
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

        print self.transitions

        self.state = self.states[STAND]
        self.next_state_index = STAND
        self.current_state_index = STAND
        self.state.setup_transition(self.transitions[(STAND, STAND)], STAND)

    def update(self, dt):
        #print self.state
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
            new_trans = self.transitions[(self.current_state_index, self.next_state_index)]
            if new_trans is not None:
                self.state.setup_transition(new_trans, self.next_state_index)
            else:
                self.current_state_index = self.next_state_index
                self.state = self.states[self.current_state_index]
                self.state.setup_transition(self.transitions[self.current_state_index, self.current_state_index],
                                            self.current_state_index)
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

def load_transitions():
    transitions = {}
    table = None
    with open(table) as table:
        macros = {}
        order = None
        state = 0
        i, j = 0, 0
        for line in table:
            if line.strip() == '---':
                state += 1
            if state == 0:
                key, val = line.split()
                macros[key] = val
            elif state == 1:
                order = line.split()
            else:
                row = line.split()
                for i in xrange(len(order)):
                    transitions[(eval(macros[order[j]]), eval(macros[order[i]]))] = row[i]
                j += 1


transitions = {
    (STAND, STAND): 'stop_cycle',
    (STAND, WALK): None,
    (WALK, STAND): 'stop',
    (WALK, WALK): 'walking',
    (STAND, CROUCH): 'Bow',
    (STAND, WALK | CROUCH): 'Bow',
    (CROUCH, STAND): None,
    (CROUCH, CROUCH): 'Bow_cycle',
    (CROUCH, CROUCH | WALK): None,
    (CROUCH | WALK, CROUCH): None,
    (CROUCH | WALK, CROUCH | WALK): 'crawl',
    (WALK, RUN): None,
    (RUN, WALK): None,
    (RUN, RUN): 'run',
    (RUN, RUN | CROUCH): 'slide',
    (RUN | CROUCH, RUN | CROUCH): 'slide_cycle',
    (RUN | CROUCH, CROUCH): 'slide_stop',
    (FALL, FALL): 'fall_cycle',
    (STAND, FALL): None,
    (WALK, FALL): None,
    (RUN, FALL): None,
    (FALL, STAND): None
}

transitions = load_transitions()


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
            try:
                self.animations[pair] = self.body.find_animation(transitions[pair])
            except KeyError:
                try:
                    ranim = self.body.find_animation(transitions[(pair[1]), pair[0]])
                    self.animations[pair] = Reversed_Animation(ranim)
                except KeyError:
                    sanim_f = self.body.find_animation(transitions[(pair[0], pair[0])])
                    sanim_t = self.body.find_animation(transitions[(pair[1], pair[1])])
                    self.animations[pair] = Smooth_Animation(sanim_f, sanim_t)
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