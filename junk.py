__author__ = 'Ecialo'
import pyglet
import items

money = pyglet.image.load('money.png')
apple = pyglet.image.load('apple.jpg')


class Money(items.Item):

    def __init__(self):
        super(Money, self).__init__(money)


class Apple(items.Item):
    def __init__(self):
        super(Apple, self).__init__(apple)

