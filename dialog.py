import pyglet
from pyglet.image import SolidColorImagePattern
from cocos.sprite import Sprite
from cocos.director import director
from collections import namedtuple
from collections import deque
from cocos.text import Label
#import consts as con
from registry.dialog import *
from registry.utility import COMPLETE



#consts = con.consts

Parz_port = pyglet.resource.image('parzalon_portrait.png')
Enemy_port = pyglet.resource.image('enemy_portrait.jpg')

Person = namedtuple('Person', ['name', 'portrait', 'text_color'])

persons_db = {'Parzalon': Person("Parzalon", Parz_port, (0, 0, 0, 255)),
              'Enemy': Person("Enemy", Enemy_port, (255, 0, 0, 255))}

fone = SolidColorImagePattern((0, 128, 128, 200)).create_image(DIALOG_WIDTH+STEP, DIALOG_HEIGHT)


def load_dialogs(filename):
    with open(filename) as source:
        #print 123
        state = NAME
        dialogs = {}
        name = None
        for line in source:
            if state is NAME:
                name = line.strip("#\n ")
                dialogs[name] = deque()
                state = LINE
            elif state is LINE and line.strip():
                a = line.strip().split(":")
                print a
                person, phrase = a
                dialogs[name].append((persons_db[person], phrase.strip("\"")))
            else:
                state = NAME
        return dialogs


class Phrase(Sprite):

    def __init__(self, person, phrase=None):
        phrase = phrase if phrase else ""
        portrait = person.portrait
        x, y = director.get_window_size()
        y = portrait.height
        pos = (x/3, y/2)
        self.duration = len(phrase)/CHARS_PER_MINUTE
        super(Phrase, self).__init__(portrait, pos)
        text = Sprite(fone)
        text.position = ((DIALOG_WIDTH+portrait.width+STEP)/2, 0)
        text.add(Label(phrase,
                 height=DIALOG_HEIGHT, width=DIALOG_WIDTH,
                 color=person.text_color, multiline=True, anchor_x='center'))
        self.add(text)

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0.0:
            return COMPLETE


class Dialog(object):

    def __init__(self, phrases=None):
        self.phrases = deque(map(lambda phrase: Phrase(*phrase),  phrases))

    def update(self, dt):
        if self.phrases and self.phrases[0].update(dt) is COMPLETE:
            return self.phrases.popleft()

    def current_phrase(self):
        return self.phrases[0]

    def num_of_phrases(self):
        return len(self.phrases)

dialogs_db = load_dialogs('dialogs.txt')


