__author__ = 'Ecialo'
import effects as eff
import consts as con

consts = con.consts


def collide_actor_actor(actor1, actor2):
    #print "push"
    if actor1.fight_group != actor2.fight_group:
        map(lambda x: x(actor1), actor2.body.on_collide_effects)
        map(lambda x: x(actor2), actor1.body.on_collide_effects)
        s_c = actor1.cshape.center
        o_c = actor2.cshape.center
        d = o_c - s_c
        l = actor1.width/2 + actor2.width/2
        dd = l - abs(d.x)
        if d.x > 0:
            actor1._move(-dd/2, 0)
            actor2._move(dd/2, 0)
        else:
            actor1._move(dd/2, 0)
            actor2._move(-dd/2, 0)


def collide_actor_hit_zone(actor, hit_zone):
    if actor.fight_group != hit_zone.base_fight_group:
        #print hit_zone
        actor.collide(hit_zone)


def collide_actor_slash(actor, slash):
    #print slash.time_to_complete
    #gr = actor.fight_group != slash.base_fight_group
    #tim = slash.time_to_complete <= 0.0
    #print "Gr Time", gr, tim
    if actor.fight_group != slash.base_fight_group and slash.time_to_complete <= 0.0:
        x, y = slash.end.x, slash.end.y
        #print x, y
        if actor.touches_point(x, y):
            actor.collide(slash)


def collide_slash_slash(slash1, slash2):
    parry(slash1, slash2)


def collide_slash_hit_zone(slash, hit_zone):
    if hit_zone.hit_shape is con.LINE:
        parry(slash, hit_zone)


def collide_hit_zone_hit_zone(hit_zone_1, hit_zone_2):
    pass


def parry(self, other):
        """
        Parry consider successful then two lines create defined angle
        """
        if self.fight_group is other.fight_group:
            return
        #self.uncompleteness = self.time_to_complete/self.master.stab_time if self.hit_pattern == con.STAB \
            #else self.time_to_complete/self.master.swing_time
        #other.uncompleteness = other.time_to_complete/other.master.stab_time if other.hit_pattern == con.STAB \
            #else other.time_to_complete/other.master.swing_time
        first = self if self.uncompleteness() < other.uncompleteness() else other
        second = self if first is other else other
        if con.STAB in second.features:
            return
        p = self.trace.intersect(other.trace)
        if p is not None and cross_angle(self.trace.v, other.trace.v) <= consts['parry_cos_disp']:
            #print eff.Sparkles.add_to_surface
            #print p
            eff.Sparkles().add_to_surface(p)
            other.complete(parried=True)
            self.complete(parried=True)


def cross_angle(v1, v2):
    """
    Calculate cos between two lines
    """
    #Cos of angle between two hit lines
    angle = abs((v1.x * v2.x + v1.y * v2.y)/(abs(v1)*abs(v2)))
    #print angle
    return angle