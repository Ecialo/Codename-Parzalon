#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Ecialo"
__date__ ="$28.08.2013 17:00:53$"
#import cocos
from collections import deque
from itertools import ifilter
from math import sqrt
from time import clock
from heapq import *

from cocos import scene
from cocos.director import *
from cocos import tiles
from cocos import layer
from cocos import draw
from pyglet.window import key
import Box2D as b2

from actor import Actor
from registry.Bodies.bodies import Human
from registry.Brains.brains import Task
from registry.Brains.brains import COMPLETE
from registry.Brains.brains import Brain
from registry.Brains.brains import Animate
import movable_object
import consts as con
from consts import tiles_to_pixels
from consts import jump_height_to_jump_speed
from location import Location_Layer
from location import b2Listener

EPS = 4.0


class Path_Method(object):

    def __init__(self, direction):
        self.direction = direction[0]

    def check(self, target):
        pass

    def _check_and_turn(self, target):
        if target.direction != self.direction:
            target.direction *= -1

    def __call__(self, master, target_cell, dt):
        self._check_and_turn(master)


class Move(Path_Method):

    def __init__(self, direction):
        super(Move, self).__init__(direction)

    def check(self, target):
        return True

    def __call__(self, master, target_cell, dt):
        super(Move, self).__call__(master, None, dt)
        Animate(master, 'walk')
        master.walk(master.direction)


class Jump(Path_Method):

    def __init__(self, speed, height, direction):
        super(Jump, self).__init__(direction)
        speed = tiles_to_pixels(speed)
        height = jump_height_to_jump_speed(height)
        self.parameters = {'speed': speed,
                           'jump_height': height}

    def check(self, target):
        return True
        #return target.speed >= self.parameters['speed'] and target.jump_height >= self.parameters['jump_height']

    def __call__(self, master, target_cell, dt):
        super(Jump, self).__call__(master, None, dt)
        master.jump()
        print master.position[0], target_cell.center[0]
        if abs(master.position[0] - target_cell.center[0]) > EPS:
            Animate(master, 'walk')
            master.walk(master.direction)
        else:
            print 2312312312
            master.stand()


class Fall(Path_Method):

    def __init__(self, speed, direction):
        super(Fall, self).__init__(direction)
        speed = tiles_to_pixels(speed)
        self.parameters = {'speed': speed}

    def check(self, target):
        return target.speed >= self.parameters['speed']

    def __call__(self, master, target_cell, dt):
        super(Fall, self).__call__(master, None, dt)
        if abs(master.position[0] - target_cell.center[0]) > EPS:
            Animate(master, 'walk')
            master.walk(master.direction)
        else:
            master.stand()


def location_preprocess(rect_map):
    UP = rect_map.UP
    DOWN = rect_map.DOWN
    LEFT = rect_map.LEFT
    RIGHT = rect_map.RIGHT

    HEIGHT = 5
    DEPTH = 8
    DISTANCE = 6
    PASSAGE_HEIGHT = 6

    connections = 'connections'
    cells = rect_map.cells

    def is_floor(cell):
        floor = rect_map.get_neighbor(cell, DOWN)
        return bool(floor) and bool(floor.get('top'))

    def is_wall(cell):
        return bool(cell.get('left')) or bool(cell.get('right'))

    def is_passage(cell):
        cur_cell = cell
        for i in xrange(PASSAGE_HEIGHT):
            if is_wall(cur_cell):
                return False
            cur_cell = rect_map.get_neighbor(cur_cell, UP)
        else:
            return True

    def check_floor_in_sector(start_cell, direction):   # direction must be LEFT or RIGHT
        cur_cell = rect_map.get_neighbor(start_cell, direction)
        if cur_cell:
            if is_floor(cur_cell) and not is_wall(cur_cell):
                yield (cur_cell, Move(direction))
            elif is_wall(cur_cell):                     # Ledge
                #print "LEEEEEEEEEEEEEEEEEEEEEEEEEEEEEDGE"
                for i in xrange(HEIGHT):
                    cur_cell = rect_map.get_neighbor(cur_cell, UP)
                    if cur_cell and not is_wall(cur_cell) and is_floor(cur_cell) and is_passage(cur_cell):
                        yield (cur_cell, Jump(1, i, direction))
                        break
            else:                                       # Hole
                already_closet_for_fall = False
                already_closest_for_skip = False
                already_closest_for_jumpover = False
                for i in xrange(DISTANCE):
                    cur_cell = rect_map.get_neighbor(cur_cell, direction)
                    if not cur_cell:
                        break
                    if not already_closest_for_skip and is_floor(cur_cell) and is_passage(cur_cell):
                        already_closest_for_skip = True
                        yield (cur_cell, Jump(i, 0, direction))

                    if not already_closet_for_fall:
                        cur_dcell = cur_cell
                        for j in xrange(DEPTH):
                            cur_dcell = rect_map.get_neighbor(cur_dcell, DOWN)
                            if cur_dcell and is_floor(cur_dcell) and is_passage(cur_dcell):
                                already_closet_for_fall = True
                                yield (cur_dcell, Fall(i, direction))
                                break

                    if not already_closest_for_jumpover:
                        cur_hcell = cur_cell
                        for j in xrange(HEIGHT):
                            cur_hcell = rect_map.get_neighbor(cur_hcell, UP)
                            if cur_hcell and not is_wall(cur_hcell) and is_floor(cur_hcell) and is_passage(cur_hcell):
                                already_closest_for_jumpover = True
                                print "SUCSESSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
                                yield (cur_hcell, Jump(i, j, direction))
                                break

    def find_and_append_cell_connections(cell, direction):
        for connection, method in check_floor_in_sector(cell, direction):
            print connection, method
            cell[connections].append((connection, method))
            #print cell[connections]

    for cell_column in cells:
        for cell in cell_column:
            cell[connections] = []
            if is_floor(cell) and is_passage(cell):
                find_and_append_cell_connections(cell, LEFT)
                #print cell[connections]
                find_and_append_cell_connections(cell, RIGHT)
    #for cell_column in cells:
    #    for cell in cell_column:
    #        print cell[connections]


def make_path(end_cell_nab):
    #print "path", end_cell_nab[-1]
    path = deque()
    current_cell_pair = end_cell_nab
    while current_cell_pair is not None:
        print "path", current_cell_pair[-2]
        path.appendleft(current_cell_pair[-2])
        current_cell_pair = current_cell_pair[-1]
    #print path
    return path


def manhattan_metric(start, end):
    return abs(start.i - end.i) + abs(start.j - end.j)


def Grankovski_euristic(start, end):
    dx = end.i - start.i
    dy = end.j - start.j
    a = 10
    return int(sqrt(dx*dx + a*dy*dy))


def bfs(start_cell, end_cell):
    connections = 'connections'
    already = set()
    queue = deque([(start_cell, None)])

    while queue:
        cell_pair = queue.popleft()
        current_cell, rest = cell_pair
        #print id(current_cell)
        if current_cell[0] is end_cell:
            return make_path(cell_pair)
        already.add(current_cell[0])
        for connection in ifilter(lambda x: x[0] not in already, current_cell[0][connections]):
            queue.append((connection, cell_pair))
    else:
        return make_path(((start_cell, None), None))


def dijkstra(metric):
    def search(start_cell, end_cell):
        connections = 'connections'
        already = set()
        queue = [(0, (start_cell, None), None)]

        while queue:
            cell_nab = heappop(queue)
            d, current_cell, track = cell_nab
            if current_cell[0] is end_cell:
                return make_path(cell_nab)
            already.add(current_cell[0])
            for connection in ifilter(lambda x: x[0] not in already, current_cell[0][connections]):
                nd = d + metric(current_cell[0], connection[0])
                heappush(queue, (nd, connection, cell_nab))
        else:
            return make_path((0, (start_cell, None), None))
    return search


manhattan_dijkstra = dijkstra(manhattan_metric)


def a_star(metric, euristic):
    def search(start_cell, end_cell):
        connections = 'connections'
        already = set()
        queue = [(euristic(start_cell, end_cell), (start_cell, None), None)]

        while queue:
            cell_nab = heappop(queue)
            d, current_cell, track = cell_nab
            if current_cell[0] is end_cell:
                return make_path(cell_nab)
            already.add(current_cell[0])
            #print current_cell[0].get(connections)
            for connection in ifilter(lambda x: x[0] not in already, current_cell[0][connections]):
                nd = d + metric(current_cell[0], connection[0]) + euristic(connection[0], end_cell)
                #print connection
                heappush(queue, (nd, connection, cell_nab))
        else:
            return make_path((0, (start_cell, None), None))
    return search


manhattan_Grankovski_a_star = a_star(manhattan_metric, Grankovski_euristic)


def create_drawed_path(path):
    path = list(path)
    print path
    if len(path) > 1:
        return Connections_Net([(path[i], path[i+1]) for i in xrange(len(path)-1)])
    else:
        return Connections_Net([(path[0], path[0])])


def net_construction(rect_map):
    pairs = []
    cells = rect_map.cells
    for cell_column in cells:
        for cell in cell_column:
            for available_neighbor in cell.get('connections'):
                pairs.append((cell, available_neighbor))
    return Connections_Net(pairs)


class Follow_To(Task):

    def __init__(self, master, path):
        super(Follow_To, self).__init__(master)
        self.path = path

    def __call__(self, dt):
        path = self.path
        if not path:
            self.master.stand()
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            return COMPLETE
        master = self.master
        x, y = self.master.cshape.center
        y -= self.master.cshape.ry
        # floor = master.get_rect().midbottom
        floor = (x, y)
        current_cell = master.tilemap.get_at_pixel(*floor)
        #print cuu
        #down = master.tilemap.get_neighbor(current_cell, (0, -1))
        #print current_cell
        #i, j = down.i, down.j
        #print i, j
        #master.tilemap.set_cell_opacity(i, j, 100)
        target_cell, method = path[0]
        if current_cell is not target_cell:
            #print method
            method(master, target_cell, dt)
        else:
            path.popleft()


class Connections_Net(draw.Canvas):

    def __init__(self, pairs):
        super(Connections_Net, self).__init__()
        self.pairs = pairs

    def render(self):
        self.set_color((255, 0, 0, 155))
        for pair in self.pairs:
            self.connect_cells(*pair)

    def connect_cells(self, fr, to):
        self.move_to(fr[0].center)
        self.line_to(to[0].center)


class Tilemap_Tester_With_Box(Location_Layer):

    is_event_handler = True
    BASE_CAMERA_SPEED = 600.0
    is_debag = False

    def __init__(self, force_ground, scroller):
        layer.ScrollableLayer.__init__(self)
        self.scroller = scroller
        self.force_ground = force_ground
        self.b2world = b2.b2World(gravity=(0, -con.GRAVITY),
                                  contactListener=b2Listener())
        self.b2level = self.b2world.CreateStaticBody()
        self._create_b2_tile_map(force_ground)
        #FROM TILEMAP TESTER
        self.camera_pos = [16*25, 16*25]
        self.keys = {key.LEFT: False,
                     key.RIGHT: False,
                     key.UP: False,
                     key.DOWN: False}
        movable_object.Movable_Object.tilemap = self.force_ground
        movable_object.Movable_Object.world = self.b2world

        self.unit = Actor(Human)
        #print self.unit.cshape
        self.unit.move_to(60, 1716)
        self.add(self.unit, z=100)
        self.unit.do(Brain())
        self.cellmap = force_ground
        #self.counter = 0
        self.path = None

        self.counter = 0
        self.fr = None

        self.schedule(self.update)

    def update(self, dt):
        floor = self.unit.get_rect().midbottom
        current_cell = self.force_ground.get_at_pixel(*floor)
        down = self.force_ground.get_neighbor(current_cell, (0, -1))
        i, j = down.i, down.j
        self.force_ground.set_cell_opacity(i, j, 100)

        self.b2world.Step(dt, 1, 1)

        self.camera_pos[0] += (self.keys[key.RIGHT] - self.keys[key.LEFT])*self.BASE_CAMERA_SPEED*dt
        self.camera_pos[1] += (self.keys[key.UP] - self.keys[key.DOWN])*self.BASE_CAMERA_SPEED*dt
        self.scroller.set_focus(*self.camera_pos)

    def on_key_press(self, symbol, modifers):
        self.keys[symbol] = True

    def on_key_release(self, symbol, modifers):
        self.keys[symbol] = False

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.is_debag:
            if self.path:
                self.path.kill()
            x, y = self.scroller.pixel_from_screen(x, y)
            to = self.cellmap.get_at_pixel(x, y)
            #fr = self.cellmap.get_neighbor(self.cellmap.get_at_pixel(*self.unit.get_rect().midbottom), self.cellmap.UP)
            fr = self.cellmap.get_at_pixel(*self.unit.get_rect().midbottom)
            #print self.cellmap.get_neighbor(fr, self.cellmap.DOWN).tile.properties
            oth_path = Connections_Net([(fr, to)])
            #self.add(oth_path, z=10)
            t = clock()
            #path = manhattan_dijkstra(self.fr, self.to)
            #path = bfs(self.fr, self.to)
            path = manhattan_Grankovski_a_star(fr, to)
            print clock() - t
            self.path = create_drawed_path(path)
            self.unit.push_task(Follow_To(self.unit, path))
            self.cellmap.add(self.path, z=10)
        else:
            if self.counter == 0:
                if self.path:
                    self.path.kill()
                x, y = self.scroller.pixel_from_screen(x, y)
                self.fr = self.cellmap.get_at_pixel(x, y)
                self.counter = 1
            else:
                x, y = self.scroller.pixel_from_screen(x, y)
                to = self.cellmap.get_at_pixel(x, y)
                path = manhattan_Grankovski_a_star(self.fr, to)
                self.path = create_drawed_path(path)
                self.cellmap.add(self.path, z=10)
                self.counter = 0

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_release(self, x, y, buttons, modifers):
        pass


if __name__ == "__main__":
    director.init(width=1024, height=768, do_not_scale=True)
    dscene = scene.Scene()
    mp = tiles.load('map01.tmx')
    #mp = tiles.load('tst_map.tmx')
    force = mp['Player Level']
    back = mp['Background']
    scroller = layer.ScrollingManager()
    lay = Tilemap_Tester_With_Box(force, scroller)
    location_preprocess(force)
    net = net_construction(force)
#    force.add(net)

    scroller.add(back, z=-1)
    scroller.add(lay, z=0)
    scroller.add(force, z=1)

    dscene.add(scroller)
    #objs = mp['Scripts']
    print force.cells[0][0]


    director.run(dscene)