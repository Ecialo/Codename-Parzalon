__author__ = 'Ecialo'
import cocos
import consts as con
import expression as ex

from cocos.layer import Layer
from cocos.director import director
from cocos.batch import BatchNode
from cocos.sprite import Sprite
from cocos.draw import Line
from pyglet.event import EventDispatcher

consts = con.consts


class ResizableLayer(Layer, EventDispatcher):
    is_event_handler = True

    def __init__(self):
        super(ResizableLayer, self).__init__()
        self.cur_x, self.cur_y = director.get_window_size()
        self.dx, self.dy = 0, 0

    def on_resize(self, width, height):
        self.dx = width - self.cur_x
        self.dy = height - self.cur_y
        self.cur_x, self.cur_y = width, height
        self.dispatch_event('on_hud_shift_needed', self.dx, self.dy)

ResizableLayer.register_event_type('on_hud_shift_needed')


class DudeDamageLayer(ResizableLayer):
    is_event_handler = True

    def __init__(self, game_layer):
        super(DudeDamageLayer, self).__init__()
        self.game_layer = game_layer
        self.red_bp = BatchNode()
        self.normal_bp = BatchNode()
        self.armored_bp = BatchNode()

        self.ui_body = {'back': {}, 'front': {}, 'armored': {}}
        self._init_body_parts('back')
        self._init_body_parts('front')
        self._init_body_parts('armored')

        # the layer now listens to on_take_damage event from hero
        self.game_layer.hero.push_handlers(self.on_take_damage)

        for body_part in self.ui_body['back']:
            self.red_bp.add(self.ui_body['back'][body_part])
        for body_part in self.ui_body['front']:
            self.normal_bp.add(self.ui_body['front'][body_part])
        for body_part in self.ui_body['armored']:
            self.armored_bp.add(self.ui_body['armored'][body_part])

        self.add(self.red_bp, z=-1)
        self.add(self.normal_bp, z=0)
        self.add(self.armored_bp, z=1)

    def _init_body_parts(self, layer_type='front'):
        self.ui_body[layer_type]['head'] = Sprite(consts['hud']['body'][layer_type]['head'])
        self.ui_body[layer_type]['head'].position = (50, self.cur_y-50)
        self.ui_body[layer_type]['chest'] = Sprite(consts['hud']['body'][layer_type]['chest'])
        self.ui_body[layer_type]['chest'].position = (50, self.cur_y-85)
        self.ui_body[layer_type]['left_arm'] = Sprite(consts['hud']['body'][layer_type]['left_arm'])
        self.ui_body[layer_type]['left_arm'].position = (34, self.cur_y-90)
        self.ui_body[layer_type]['right_arm'] = Sprite(consts['hud']['body'][layer_type]['right_arm'])
        self.ui_body[layer_type]['right_arm'].position = (66, self.cur_y-91)
        self.ui_body[layer_type]['legs'] = Sprite(consts['hud']['body'][layer_type]['legs'])
        self.ui_body[layer_type]['legs'].position = (50, self.cur_y-119)

    def on_hud_shift_needed(self, dx, dy):
        for layer_type in ('back', 'front', 'armored'):
            for body_part in self.ui_body[layer_type]:
                self.ui_body[layer_type][body_part].y += dy

    def on_take_damage(self, body_part):
        armor_damage = False
        if body_part.slot >= con.ARMOR:
            slot = body_part.slot - con.ARMOR
            armor_damage = True
        else:
            slot = body_part.slot

        body_parts = {con.HEAD: 'head',
                      con.CHEST: 'chest',
                      con.LEGS: 'legs'}

        if slot in body_parts:
            bp_name = body_parts[slot]
        else:
            bp_name = 'right_arm'  # why not?

        if armor_damage:
            self.ui_body['armored'][bp_name].opacity = 255.0 * body_part.armor / body_part.max_armor
        else:
            self.ui_body['front'][bp_name].opacity = 255.0 * body_part.health / body_part.max_health


class DudeStatusLayer(ResizableLayer):
    is_event_handler = True

    def __init__(self, game_layer):
        super(DudeStatusLayer, self).__init__()
        self.game_layer = game_layer
        self.batch = BatchNode()

        self.ui_status_icons = {'health_icon': Sprite(consts['hud']['status']['health_icon'],
                                                      position=(110, self.cur_y-50))}

        self.bar_orig_x = 140
        self.hb_len = 100  # health bar length
        self.ui_health_bar = Line((self.bar_orig_x, self.cur_y-50),
                                  (self.bar_orig_x + self.hb_len, self.cur_y-50),
                                  (255, 0, 0, 255), 15)

        # the layer now listens to on_take_damage event from hero
        self.game_layer.hero.push_handlers(self.on_take_damage)

        for icon in self.ui_status_icons:
            self.batch.add(self.ui_status_icons[icon])
        self.add(self.batch)

        self.add(self.ui_health_bar)

    def on_hud_shift_needed(self, dx, dy):
        for icon in self.ui_status_icons:
            self.ui_status_icons[icon].y += dy
        self.ui_health_bar.y += dy

    def on_take_damage(self, body_part):
        hb = self.ui_health_bar
        hb.end = (self.bar_orig_x +
                  self.hb_len * body_part.master.health / float(body_part.master.max_health),
                  self.cur_y-50)


class HUD(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, game_layer):
        self.game_layer = game_layer
        super(HUD, self).__init__()
        self.game_layer.script_manager.set_handler('run_dialog', self.run_dialog)
        self.current_dialog = None
        self.add(DudeDamageLayer(game_layer))
        self.add(DudeStatusLayer(game_layer))

    def run_dialog(self, dialog_name, actor, location):
        print "DIALOGS"
        self.current_dialog = ex.Dialog(ex.dialogs_db[dialog_name])
        self.add(self.current_dialog.current_phrase())
        self.schedule(self.show_dialog)

    def show_dialog(self, dt):
        phrase = self.current_dialog.update(dt)
        if phrase:
            self.remove(phrase)
            if self.current_dialog.num_of_phrases() == 0:
                self.unschedule(self.show_dialog)
                self.current_dialog = None
            else:
                self.add(self.current_dialog.current_phrase())

    def on_exit(self):
        self.game_layer.script_manager.remove_handler('run_dialog', self)