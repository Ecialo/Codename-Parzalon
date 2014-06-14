# -*- coding: utf-8 -*-
__author__ = 'ecialo'
import Box2D as b2


class Abstract_Map_Object(object):

    def __init__(self, properties, x, y):
        self.position = (x, y)
        self.properties = properties
        self.b2body = None

    def to_b2(self, b2World):
        u"""
        Отправляет объект в b2World. Какой именно формы объект уточняется в реализации
        """
        pass

    def _to_b2(self, b2World, shape):
        self.b2body = b2World.CreateStaticBody(userData=self, position=self.position)
        self.b2body.CreateFixture(b2.b2FixtureDef(shape=shape))

    def __getitem__(self, item):
        return self.properties[item]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __contains__(self, item):
        return item in self.properties


class Polyline_Map_Object(Abstract_Map_Object):

    def __init__(self, properties, points, name="", type='', x=0, y=0):
        super(Polyline_Map_Object, self).__init__(properties, x, y)
        self.points = list(points)
        self.name = name
        self.type = type

    def to_b2(self, b2World):
        shape = b2.b2ChainShape(vertices=self.points)
        #shape.CreateChain(self.points, len(self.points))
        super(Polyline_Map_Object, self)._to_b2(b2World, shape)

    def __str__(self):
        return "Polyline\nname\t%s\ntype\t%s\nx,y\t%f,%f\nPoints\n" % (self.name, self.type, self.position[0], self.position[1]) +\
               str(list(self.points)) + "\n" + str(self.properties)


class Polygon_Map_Object(Abstract_Map_Object):

    def __init__(self, properties, points, name="", type='', x=0, y=0):
        super(Polygon_Map_Object, self).__init__(properties, x, y)
        #TODO Проверить полигон на выпуклость и расположение точек против часовой стрелки
        self.points = list(points)
        self.name = name
        self.type = type

    def to_b2(self, b2World):
        shape = b2.b2PolygonShape(vertices=self.points)
        super(Polygon_Map_Object, self)._to_b2(b2World, shape)

    def __str__(self):
        return "Polygon\nname\t%s\ntype\t%s\nx,y\t%f,%f\nPoints\n" % (self.name, self.type, self.position[0], self.position[1]) +\
               str(list(self.points))+ "\n" + str(self.properties)


class Tile_Map_Object(Abstract_Map_Object):

    def __init__(self, properties, gid=0, name="", type='', x=0, y=0):
        super(Tile_Map_Object, self).__init__(properties, x, y)
        self.gid = gid
        self.name = name
        self.type = type

    def to_b2(self, b2World):
        pass

    def __str__(self):
        return "Tile\nname\t%s\ntype\t%s\nx,y\t%f,%f" % (self.name, self.type, self.position[0], self.position[1])+ \
               "\n" + str(self.properties)


class Rect_Map_Object(Abstract_Map_Object):

    def __init__(self, properties, name="", type='', x=0, y=0, width=0, height=0):
        super(Rect_Map_Object, self).__init__(properties, x, y)
        self.name = name
        self.type = type
        self.width = width
        self.height = height

    def to_b2(self, b2World):
        shape = b2.b2PolygonShape()
        shape.SetAsBox(self.width/2, self.height/2, self.position, 0)
        super(Rect_Map_Object, self)._to_b2(b2World, shape)

    def __str__(self):
        return "Rect\nname\t%s\ntype\t%s\nx,y\t%f,%f\nWidth\t%f,%f" % \
               (self.name, self.type, self.position[0], self.position[1], self.width, self.height) + "\n" + str(self.properties)


class Map_Object(object):

    def __init__(self, base, properties, tile_sizes, map_sizes=None):
        u"""
        Если мы уточняем размеры карты => данные не подготовлены => их нужно подготовить
        """
        self.base = base
        self.properties = properties
        self.tile_sizes = tile_sizes
        self.is_prepared = map_sizes is None
        if not self.is_prepared:
            tile_width, tile_height = tile_sizes
            map_width, map_height = map_sizes
            self.base['x'] = float(base['x'])/tile_width
            self.base['y'] = map_height - float(base['y'])/tile_height

    def prepare_points(self, points):
        tile_height, tile_width = self.tile_sizes
        if type(points) is str:
            points = points.split()
        for point in points:
            ppoint = point.split(',')
            yield float(ppoint[0])/tile_width, -float(ppoint[1])/tile_height

    def create_polyline(self, points):
        if not self.is_prepared:
            points = self.prepare_points(points)
        return Polyline_Map_Object(self.properties, points, **self.base)

    def create_polygon(self, points):
        if not self.is_prepared:
            points = self.prepare_points(points)
        return Polygon_Map_Object(self.properties, points, **self.base)

    def create_tile(self):
        return Tile_Map_Object(self.properties, **self.base)

    def create_rect(self):
        tile_width, tile_height = self.tile_sizes
        if not self.is_prepared:
            self.base['width'] = float(self.base['width'])/tile_width
            self.base['height'] = float(self.base['height'])/tile_height
        return Rect_Map_Object(self.properties, **self.base)