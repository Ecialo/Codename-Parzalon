# -*- coding: utf-8 -*-
"""
Что эта хрень должна уметь:
1) Применять анимацию+действие по ключу.
2) В зависимости от состояний актёра менять анимацию от вызовов(большая скорость - бег, маленькая - ходьба)
3) Переключать состояния

Существую след действия:
1) Подвигаться
2) Прыгнуть
3) Присесть
4) Использовать предмет(руки, режимы).
6) Сменить комплекты
7) Сменить актив предмет на поясе
8) Активировать фиговину в точке

Все действия доступны игроку, не все монстрякам.

Состояния:
1) Стоит
2) В присяде
3) Идёт
4) Бежит
5) Прыгает
5) В полёте
6) Огребает

Стоит/Идёт/Бежит зависят от скорости

Идёт + В присяде = Идёт в присяде
Бежит + В Присяде = Скользит/перекатывается (если оно нам надо)
Стоит + Прыгает = Высокий прыжок => В полёте
Идёт + Прыгает = Длинный прыжок => В полёте
Бежит + Прыгает = Длинный прыжок => В полёте

Огребает + В полёте = Отлетает
Огребает + В скольжении = Отлетает
Огребает + В присяде = Огребает в присяде (\:D/)

Предметы доступны к использованию если чел не огребает.

Я искренне верю, что если грамотно использовать смешивание анимации и раздельное анимирование рук и корпуса при использовании,
предметов, можно будет достичь хорошего результата за разумное время.

"""
__author__ = 'ecialo'
from registry.utility import binary_list
STAND, WALK = binary_list(2)
COUNTER_DIRECTION = -1


class State(object):

    name = None

    def __init__(self, actor):
        self.actor = actor
        self.body = actor.body
        self.b2body = actor.b2body
        if self.name:
            self.animation = self.body.find_animation(self.name)
        else:
            self.animation = None
        self.time = 0.0

    def move(self, direction):
        pass

    def crouch(self):
        pass

    def jump(self):
        pass

    def take_hit(self):
        pass

    def update(self, dt):
        self.time += dt
        if self.animation:
            self.animation.apply(time=self.time,
                                 skeleton=self.body,
                                 loop=True)
        self.body.skeleton_data.update_transform()


class Stand(State):

    def move(self, direction):
        if direction:
            if self.actor.direction != direction:
                self.actor.direction *= COUNTER_DIRECTION
            return WALK
        return 0


class Walk(State):

    name = 'walking'

    def move(self, direction):
        if self.actor.direction != direction:
            return STAND
        return 0

    def update(self, dt):
        super(Walk, self).update(dt)
        self.actor.b2body.ApplyForceToCenter((15*self.actor.direction, 0), 1)


class State_Machine(object):

    def __init__(self, actor):
        self.states = {STAND: Stand(actor),
                       WALK: Walk(actor)}
        self.state = self.states[STAND]
        self.next_state = STAND

    def update(self, dt):
        #print self.state
        self.state.update(dt)
        if self.next_state:
            self.state.time = 0.0
            self.state = self.states[self.next_state]
        self.next_state = 0

    def move(self, direction):
        self.next_state |= self.state.move(direction)

    def jump(self):
        self.state.jump()

    def crouch(self):
        self.state.crouch()

    def take_hit(self):
        self.state.take_hit()