__author__ = 'Ecialo'

from cocos.batch import BatchableNode
from cocos.sprite import Sprite
from cocos import euclid as eu

import Box2D as b2

from registry.metric import pixels_to_tiles
from registry.metric import tiles_to_pixels


#TODO: move fixture adding to more specific classes
class Movable_Object(Sprite):

    tilemap = None
    world = None

    def __init__(self, img=None, cshape=None, position=(0, 0), vertical_speed=0.0, horizontal_speed=0.0):
        if img:
            super(Movable_Object, self).__init__(img, position)
            self.image = img
        else:
            BatchableNode.__init__(self)
        # self.cshape = cshape
        # if cshape:
        #     self.cshape.center = eu.Vector2(*position)
        self.b2body = None
        self.setup_b2body()
        print "MOVA", position
        self.b2body.linearVelocity = pixels_to_tiles((horizontal_speed, vertical_speed))
        self.b2body.position = position
        print self.b2body.position, "TRUE"

        self.ground_count = 0
        self.on_ground = False

    def setup_b2body(self):
        self.b2body = self.world.CreateDynamicBody(fixedRotation=True, userData=self, allowSleep=False)

    def set_position(self, position):
        val = tiles_to_pixels(position)
        self.position = val
        #self.cshape.center = val

    def transfer(self):
        to_transfer = {'fixedRotation': 'fixedRotation',
                       'userData': 'userData',
                       'sleepingAllowed': 'allowSleep'}
        transfer_dict = {}
        for old_name, new_name in to_transfer.items():
            transfer_dict[new_name] = eval('self.b2body.'+old_name)
        new_b2body = self.world.CreateDynamicBody(**transfer_dict)
        for fixture in self.b2body.fixtures:
            to_transfer = {'filterData': 'filter',
                           'friction': 'friction',
                           'sensor': 'isSensor',
                           'userData': 'userData',
                           'shape': 'shape'}
            transfer_dict = {}
            for old_name, new_name in to_transfer.items():
                transfer_dict[new_name] = eval('fixture.'+old_name)
            def_fix = b2.b2FixtureDef(**transfer_dict)
            new_fixture = new_b2body.CreateFixture(def_fix)
            handlers = self.b2body.cool_world.true_listener.getHandlers(fixture)
            if handlers:
                self.b2body.cool_world.true_listener.removeEventHandler(fixture)
                self.world.addEventHandler(new_fixture, *handlers)
        self.b2body.cool_world.destroy_body(self.b2body)
        self.b2body = new_b2body

    def onGroundBegin(self, fixture):
        self.ground_count += 1
        self.on_ground = True

    def onGroundEnd(self, fixture):
        self.ground_count -= 1
        if self.ground_count == 0:
            self.on_ground = False

    def update(self, dt):
        self.set_position(self.b2body.position)


class Concrete_Movable_Object(Sprite):
    pass


class Abstarct_Movable_Object(BatchableNode):
    pass