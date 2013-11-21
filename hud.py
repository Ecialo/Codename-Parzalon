__author__ = 'Ecialo'
import cocos
import consts as con
consts = con.consts


class HUD(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self, game_layer):
        self.game_layer = game_layer
        super(HUD, self).__init__()
        sp = cocos.sprite.Sprite(consts['img']['helmet'])
        sp.position = (40, 40)

        self.add(sp, z=5)