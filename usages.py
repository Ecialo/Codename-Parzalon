__author__ = 'Ecialo'
from cocos import euclid as eu
import hits as hit
import consts as con


def interval_proection(point, interval):
    """
    Return point in interval closet to given
    """
    if interval[0] <= point < interval[1]:
        return point
    elif point < interval[0]:
        return interval[0]
    else:
        return interval[1]


class Usage(object):

    owner = property(lambda self: self.master.master)

    def __call__(self, master):
        self.master = master
        return self

    def start_use(self, *args):
        pass

    def continue_use(self, *args):
        pass

    def end_use(self, *args):
        pass

    def move(self, v):
        pass

    def complete(self):
        self.master.available = True
        self.master.on_use = False


class Throw(Usage):

    def __init__(self, effects):
        self.effects = effects
        self.actual_hit = None

    def start_use(self, *args):
        pass

    def continue_use(self, *args):
        pass

    def end_use(self, *args):
        end_point = eu.Vector2(*args[0])
        v = end_point - self.owner.cshape.center
        hit_zone = hit.Hit_Zone(self, self.master.image, v, 300, self.owner.position)
        self.actual_hit = hit_zone
        self.master.dispatch_event('on_launch_missile', hit_zone)
        hit_zone.show_hitboxes()
        self.owner.hands.remove(self.master)
        self.master.on_use = False
        self.master.available = True

    def destroy_missile(self, missile):
        self.master.dispatch_event('on_remove_missile', missile)


class Swing(Usage):

    def __init__(self, effects, hit_pattern):

        self.hit_pattern = hit_pattern
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
        self.actual_hit = hit.Slash(stp, end, self, self.hit_pattern)
        self.master.dispatch_event('on_do_hit', self.actual_hit)

    def continue_use(self, *args):
        """
        Define new end point
        """
        end_point = args[0]
        start_point = self.actual_hit.start
        vec = end_point - start_point
        end = start_point + vec.normalize()*self.length
        self.actual_hit.end = end

    def end_use(self, *args):
        """
        Create full collidable obj from line and memor what attack is going on
        """
        self.master.available = False
        self.actual_hit.perform(self.swing_time)
        self.master.dispatch_event('on_perform_hit', self.actual_hit)

    def complete(self):
        if self.actual_hit is not None:
            self.master.dispatch_event('on_remove_hit', self.actual_hit)
            self.actual_hit = None
            self.master.available = True
            self.master.on_use = False

    def move(self, v):
        #print 111
        if self.actual_hit is not None:
            self.actual_hit._move(v)


class Chop(Swing):

    def __init__(self, effects):
        Swing.__init__(self, effects, hit_pattern=con.CHOP)


class Stab(Swing):

    def __init__(self, effects):
        Swing.__init__(self, effects, hit_pattern=con.STAB)


class Shoot(Usage):

    def __init__(self, effects, bullet_image):
        self.bullet_image = bullet_image
        self.effects = effects

    def end_use(self, *args):
        if self.master.ammo > 0:
            end_point = eu.Vector2(*args[0])
            v = end_point - self.owner.cshape.center
            hit_zone = hit.Hit_Zone(self, self.bullet_image, v, 300, self.owner.position)
            self.actual_hit = hit_zone
            self.master.dispatch_event('on_launch_missile', hit_zone)
            hit_zone.show_hitboxes()
            self.master.on_use = False
            self.master.available = True
            self.master.ammo -= 1

    def destroy_missile(self, missile):
        self.master.dispatch_event('on_remove_missile', missile)