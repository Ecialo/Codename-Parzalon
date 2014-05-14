from registry.Effects import on_hit_effects as on_h

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


# class Usage(object):
#
#     owner = property(lambda self: self.master.master)
#
#     def __call__(self, master):
#         self.master = master
#         return self
#
#     def start_use(self, *args):
#         pass
#
#     def continue_use(self, *args):
#         pass
#
#     def end_use(self, *args):
#         pass
#
#     def move(self, v):
#         pass
#
#     def complete(self):
#         self.master.available = True
#         self.master.on_use = False


# class Throw(Usage):
#
#     def __init__(self, effects):
#         self.effects = effects
#         self.actual_hit = None
#
#     def start_use(self, *args):
#         pass
#
#     def continue_use(self, *args):
#         pass
#
#     def end_use(self, *args):
#         end_point = eu.Vector2(*args[0])
#         v = end_point - self.owner.cshape.center
#         hit_zone = hit.Missile(self, self.master.image, v, 300, self.owner.position, con.LINE)
#         self.actual_hit = hit_zone
#         self.master.dispatch_event('on_launch_missile', hit_zone)
#         #hit_zone.show_hitboxes()
#         #self.owner.hands.remove(self.master)
#         self.owner.hands.remove(self.master)
#         self.master.on_use = False
#         self.master.available = True
#         self.master.length -= 1
#
#     def destroy_missile(self, missile):
#         self.master.dispatch_event('on_remove_missile', missile)


# class Swing(Usage):
#
#     def __init__(self, effects):
#
#         self.effects = effects
#         self.actual_hit = None
#         self.swing_time = 0.5
#
#     length = property(lambda self: self.master.length)
#
#     def start_use(self, *args):
#         """
#         Create line what start from closest to start point possible place near Actor.
#         """
#         #Define start point of hit line on screen
#         start_point = args[0]
#         if isinstance(start_point, eu.Vector2):
#             stp = start_point.copy()
#         else:
#             stp = eu.Vector2(*start_point)
#         stp = self.owner.from_global_to_self(stp)
#         stp.x = stp.x/abs(stp.x) if stp.x != 0 else 0
#         stp.x *= self.owner.width/2
#         stp.y = interval_proection(stp.y, (-self.owner.height/2,
#                                            self.owner.height/2))
#         stp = self.owner.from_self_to_global(stp)
#         #Define end point of hit line on screen
#         vec = start_point - stp
#         end = stp + vec.normalize()*self.length
#         #Send line to holder in weapon for update end point and to screen for draw
#         self.actual_hit = hit.Swing(stp, end, self)
#         #self.master.dispatch_event('on_do_hit', self.actual_hit)
#         print "!232312", self.owner
#         self.owner.add(self.actual_hit, z=100)
#
#     def continue_use(self, *args):
#         """
#         Define new end point
#         """
#         end_point = self.owner.from_global_to_self(eu.Vector2(*args[0]))
#         start_point = self.actual_hit.start
#         vec = end_point - start_point
#         end = start_point + vec.normalize()*self.length
#         self.actual_hit.aim(vec)
#
#     def end_use(self, *args):
#         """
#         Create full collidable obj from line and memor what attack is going on
#         """
#         self.master.available = False
#         self.actual_hit.perform(self.swing_time)
#         self.master.dispatch_event('on_perform_hit', self.actual_hit)
#
#     def complete(self):
#         if self.actual_hit is not None:
#             print "send to remove", self.actual_hit
#             #self.master.dispatch_event('on_remove_hit', self.actual_hit)
#             print "removed"
#             self.actual_hit = None
#             self.master.available = True
#             self.master.on_use = False
#
#     def move(self, v):
#         #print 111
#         if self.actual_hit is not None:
#             self.actual_hit._move(v)


# class Chop(Swing):
#
#     def __init__(self, effects):
#         effects.append(on_h.chop)
#         Swing.__init__(self, effects)


# class Stab(Swing):
#
#     def __init__(self, effects):
#         effects.append(on_h.stab)
#         Swing.__init__(self, effects)


class Punch(Swing):

    def __init__(self, effects):
        Swing.__init__(self, effects)


# class Shoot(Usage):
#
#     def __init__(self, effects, bullet_image):
#         self.bullet_image = bullet_image
#         self.effects = effects
#
#     # def start_use(self, *args):
#     #     print 99999999999
#     #     self.master.available = False
#
#     def end_use(self, *args):
#         if self.master.ammo:
#             print 2312312321321312321
#             end_point = eu.Vector2(*args[0])
#             v = end_point - self.owner.cshape.center
#             hit_zone = hit.Missile(self, self.bullet_image, v, 300, self.owner.position, con.LINE)
#             self.actual_hit = hit_zone
#             self.master.dispatch_event('on_launch_missile', hit_zone)
#             hit_zone.show_hitboxes()
#             self.master.on_use = False
#             self.master.ammo -= 1
#             print self.master.ammo
#             if self.master.ammo > 0:
#                 self.master.available = False
#                 self.master.cur_reload = self.master.reload_time
#
#     def destroy_missile(self, missile):
#         self.master.dispatch_event('on_remove_missile', missile)