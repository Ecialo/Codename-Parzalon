# -*- coding: utf-8 -*-
__author__ = 'Ecialo'

class Swing(Usage):

    def __init__(self, effects):

        self.effects = effects
        self.actual_hit = None
        self.swing_time = 0.5

    length = property(lambda self: self.master.length)

    def start_use(self, *args):
        """
        Create line what start from closest to start point possible place near Actor.
        """
        #Define start point of hit line on screen
        start_point = args[0]
        if isinstance(start_point, eu.Vector2):
            stp = start_point.copy()
        else:
            stp = eu.Vector2(*start_point)
        stp = self.owner.from_global_to_self(stp)
        stp.x = stp.x/abs(stp.x) if stp.x != 0 else 0
        stp.x *= self.owner.width/2
        stp.y = interval_proection(stp.y, (-self.owner.height/2,
                                           self.owner.height/2))
        stp = self.owner.from_self_to_global(stp)
        #Define end point of hit line on screen
        vec = start_point - stp
        end = stp + vec.normalize()*self.length
        #Send line to holder in weapon for update end point and to screen for draw
        self.actual_hit = hit.Swing(stp, end, self)
        #self.master.dispatch_event('on_do_hit', self.actual_hit)
        print "!232312", self.owner
        self.owner.add(self.actual_hit, z=100)

    def continue_use(self, *args):
        """
        Define new end point
        """
        end_point = self.owner.from_global_to_self(eu.Vector2(*args[0]))
        start_point = self.actual_hit.start
        vec = end_point - start_point
        end = start_point + vec.normalize()*self.length
        self.actual_hit.aim(vec)

    def end_use(self, *args):
        """
        Create full collidable obj from line and memor what attack is going on
        """
        self.master.available = False
        self.actual_hit.perform(self.swing_time)
        self.master.dispatch_event('on_perform_hit', self.actual_hit)

    def complete(self):
        if self.actual_hit is not None:
            print "send to remove", self.actual_hit
            #self.master.dispatch_event('on_remove_hit', self.actual_hit)
            print "removed"
            self.actual_hit = None
            self.master.available = True
            self.master.on_use = False

    def move(self, v):
        #print 111
        if self.actual_hit is not None:
            self.actual_hit._move(v)