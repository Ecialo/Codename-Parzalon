__author__ = 'Ecialo'
from cocos.tiles import RectMap
from cocos.layer import Layer
from itertools import chain
import pyglet
from pyglet.gl import *


class No_Scroll_Map_Layer(Layer):

    def __init__(self, properties):
        self._sprites = {}
        self.properties = properties
        self.batch = pyglet.graphics.Batch()
        super(No_Scroll_Map_Layer, self).__init__()

    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.properties[key] = value

    def get(self, key, default=None):
        return self.properties.get(key, default)

    def set_dirty(self):
        # re-calculate the sprites to draw for the view
        self._sprites.clear()
        self._update_sprite_set()

    def get_all_cells(self):
        # XXX refactor me away
        return chain(*self.cells)

    def set_cell_opacity(self, i, j, opacity):
        key = self.cells[i][j].origin[:2]
        if key in self._sprites:
            self._sprites[key].opacity = opacity

    def set_cell_color(self, i, j, color):
        key = self.cells[i][j].origin[:2]
        if key in self._sprites:
            self._sprites[key].color = color

    def _update_sprite_set(self):
        # update the sprites set
        keep = set()
        for cell in self.get_all_cells():
            cx, cy = key = cell.origin[:2]
            #print cx, cy
            keep.add(key)
            if cell.tile is None:
                continue
            if key not in self._sprites:
                #print cell.tile.image
                self._sprites[key] = pyglet.sprite.Sprite(cell.tile.image,
                    x=cx, y=cy, batch=self.batch)
            s = self._sprites[key]
            # if self.debug:
            #     if getattr(s, '_label', None): continue
            #     label = [
            #         'cell=%d,%d'%(cell.i, cell.j),
            #         'origin=%d,%d px'%(cx, cy),
            #     ]
            #     for p in cell.properties:
            #         label.append('%s=%r'%(p, cell.properties[p]))
            #     lx, ly = cell.topleft
            #     s._label = pyglet.text.Label(
            #         '\n'.join(label), multiline=True, x=lx, y=ly,
            #         bold=True, font_size=8, width=cell.width,
            #         batch=self.batch)
            # else:
            #     s._label = None
            s._label = None
        for k in list(self._sprites):
            if k not in keep and k in self._sprites:
                print self._sprites[k]
                self._sprites[k]._label = None
                #del self._sprites[k]
                self._sprites[k].delete()

    def update_cell(self, cell):
        cx, cy = key = cell.origin[:2:]
        if key in self._sprites:
            self._sprites[key].delete()
        if cell.tile:
            self._sprites[key] = pyglet.sprite.Sprite(cell.tile.image, x=cx, y=cy, batch=self.batch)

    def find_cells(self, **requirements):
        '''Find all cells that match the properties specified.

        For example:

           map.find_cells(player_start=True)

        Return a list of Cell instances.
        '''
        r = []
        for col in self.cells:
            for cell in col:
                for k in requirements:
                    if cell.get(k) != requirements[k]:
                        break
                else:
                    r.append(cell)
        return r

    def on_enter(self):
        #self._update_sprite_set()
        super(No_Scroll_Map_Layer, self).on_enter()

    def draw(self):
        # invoked by Cocos machinery
        super(No_Scroll_Map_Layer, self).draw()

        # XXX overriding draw eh?
        glPushMatrix()
        self.transform()
        self.batch.draw()
        glPopMatrix()


class No_Scroll_Rect_Map_Layer(RectMap, No_Scroll_Map_Layer):
    def __init__(self, id, tw, th, cells, origin=None, properties=None):
        RectMap.__init__(self, id, tw, th, cells, origin, properties)
        No_Scroll_Map_Layer.__init__(self, properties)
        self._update_sprite_set()

    # def get_at_pixel(self, x, y):
    #     print int((x - self.origin_x) // self.tw), int((y - self.origin_y) // self.th)
    #     return RectMap.get_at_pixel(self, x, y)
