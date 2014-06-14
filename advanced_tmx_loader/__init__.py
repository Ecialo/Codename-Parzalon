# -*- coding: utf-8 -*-
__author__ = 'ecialo'
from cocos.tiles import *
from map_object import *


def load_tmx(filename):
    '''Load some tile mapping resources from a TMX file.
    '''

    resource = Resource(filename)

    tree = ElementTree.parse(resource.path)
    map = tree.getroot()
    if map.tag != 'map':
        raise ResourceError('document is <%s> instead of <map>'%
            map.name)

    width = int(map.attrib['width'])
    height  = int(map.attrib['height'])

    # XXX this is ASSUMED to be consistent
    tile_width = int(map.attrib['tilewidth'])
    tile_height = int(map.attrib['tileheight'])

    # load all the tilesets
    tilesets = []
    for tag in map.findall('tileset'):
        if 'source' in tag.attrib:
            firstgid = int(tag.attrib['firstgid'])
            path = resource.find_file(tag.attrib['source'])
            with open(path) as f:
                tag = ElementTree.fromstring(f.read())
        else:
            firstgid = int(tag.attrib['firstgid'])

        name = tag.attrib['name']

        for c in tag.getchildren():
            if c.tag == "image":
                # create a tileset from the image atlas
                path = resource.find_file(c.attrib['source'])
                tileset = TileSet.from_atlas(name, firstgid, path, tile_width, tile_height)
                # TODO consider adding the individual tiles to the resource?
                tilesets.append(tileset)
                resource.add_resource(name, tileset)
            elif c.tag == 'tile':
                # add properties to tiles in the tileset
                gid = tileset.firstgid + int(c.attrib['id'])
                tile = tileset[gid]
                props = c.find('properties')
                if props is None:
                    continue
                for p in props.findall('property'):
                    # store additional properties.
                    name = p.attrib['name']
                    value = p.attrib['value']
                    # TODO consider more type conversions?
                    if value.isdigit():
                        value = int(value)
                    tile.properties[name] = value

    # now load all the layers
    for layer in map.findall('layer'):
        data = layer.find('data')
        if data is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)

        data = data.text.strip()
        data = data.decode('base64').decode('zlib')
        data = struct.unpack('<%di' % (len(data)/4,), data)
        assert len(data) == width * height

        cells = [[None] * height for x in range(width)]
        for n, gid in enumerate(data):
            if gid < 1:
                tile = None
            else:
                # UGH
                for ts in tilesets:
                    if gid in ts:
                        tile = ts[gid]
                        break
            i = n % width
            j = height - (n // width + 1)
            cells[i][j] = RectCell(i, j, tile_width, tile_height, {}, tile)

        id = layer.attrib['name']

        # Load properties of layers
        sl = {}
        for prop in layer.getiterator('property'):
            sl[prop.attrib['name']] = prop.attrib['value']

        m = RectMapLayer(id, tile_width, tile_height, cells, None, sl)
        m.visible = int(layer.attrib.get('visible', 1))

        resource.add_resource(id, m)

    #Load objects and convert this to map objects
    width, height = float(width), float(height)
    tile_height, tile_width = float(tile_height), float(tile_width)
    for obj_group in map.findall('objectgroup'):
        id = obj_group.attrib['name']
        objs = []
        for c in obj_group.getiterator('object'):
            if c.find('ellipse') is not None:
                continue
            base = c.attrib.copy()
            properties = {}
            props = c.find('properties')
            if props is not None:
                for p in props.findall('property'):
                    properties[p.attrib['name']] = p.attrib['value']
            obj = Map_Object(base, properties, (tile_width, tile_height), (width, height))
            polygon = c.find('polygon')
            polyline = c.find('polyline')
            if 'gid' in base:
                obj = obj.create_tile()
            elif polygon is not None:
                obj = obj.create_polygon(polygon.attrib['points'])
            elif polyline is not None:
                obj = obj.create_polyline(polyline.attrib['points'])
            else:
                obj = obj.create_rect()
            objs.append(obj)
                # params = [c.attrib['x'],
                #           c.attrib['y'],
                #           c.attrib['width'],
                #           c.attrib['height']]
                # #print params
                # n = c.attrib['name'] if 'name' in c.attrib else None
                # t = c.attrib['type'] if 'type' in c.attrib else None
                # properties = {}
                # for prop in c.getiterator('property'):
                #     properties[prop.attrib['name']] = prop.attrib['value']
                # objs.append(Collision_object(n, t, cm.AARectShape, params, m_he,
                #                                 properties))

        resource.add_resource(id, objs)
    return resource

if __name__ == '__main__':
    from cocos.director import director
    from Box2D import b2World
    director.init()
    test_map_loader = load_tmx('test_loader.tmx')
    scripts = test_map_loader['Scripts']
    print scripts
    for script in scripts:
        print script
    b2world = b2.b2World()
    for script in scripts:
        script.to_b2(b2world)