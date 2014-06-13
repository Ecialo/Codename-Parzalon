import effects as eff

__author__ = 'Ecialo'
from registry.group import STAB, LINE
from registry.something import PARRY_WINDOW


def collide_actor_actor(actor1, actor2):
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
        actor.collide(hit_zone)


def collide_actor_slash(actor, slash):
    if actor.fight_group != slash.base_fight_group and slash.time_to_complete <= 0.0:
        x, y = slash.end.x, slash.end.y
        if actor.touches_point(x, y):
            actor.collide(slash)


def collide_slash_slash(slash1, slash2):
    parry(slash1, slash2)


def collide_slash_hit_zone(slash, hit_zone):
    if hit_zone.hit_shape is LINE:
        parry(slash, hit_zone)


def collide_hit_zone_hit_zone(hit_zone_1, hit_zone_2):
    pass


def parry(self, other):
        """
        Parry consider successful then two lines create defined angle
        """
        if self.fight_group is other.fight_group:
            return
        first = self if self.uncompleteness() < other.uncompleteness() else other
        second = self if first is other else other
        if STAB in second.features:
            return
        p = self.trace.intersect(other.trace)
        if p is not None and cross_angle(self.trace.v, other.trace.v) <= PARRY_WINDOW:
            eff.Sparkles().add_to_surface(p)
            other.complete(parried=True)
            self.complete(parried=True)


def cross_angle(v1, v2):
    """
    Calculate cos between two lines
    """
    angle = abs((v1.x * v2.x + v1.y * v2.y)/(abs(v1)*abs(v2)))
    return angle