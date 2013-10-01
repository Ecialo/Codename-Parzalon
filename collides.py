__author__ = 'Ecialo'


def collide_actor_actor(actor1, actor2):
    #print "push"
    if actor1.fight_group != actor2.fight_group:
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
        #print 21231
        actor.take_hit(hit_zone)


def collide_actor_slash(actor, slash):
    #print slash.time_to_complete
    #gr = actor.fight_group != slash.base_fight_group
    #tim = slash.time_to_complete <= 0.0
    #print "Gr Time", gr, tim
    if actor.fight_group != slash.base_fight_group and slash.time_to_complete <= 0.0:
        x, y = slash.end.x, slash.end.y
        #print x, y
        if actor.touches_point(x, y):
            actor.take_hit(slash)


def collide_slash_slash(slash1, slash2):
    slash1.parry(slash2)


def collide_slash_hit_zone(slash, hit_zone):
    pass


def collide_hit_zone_hit_zone(hit_zone_1, hit_zone_2):
    pass