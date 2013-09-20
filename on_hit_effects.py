__author__ = 'Ecialo'

def damage(value):
    def mast_damage(master):
        def fab_damage(body_part):
            if body_part.armor > value:
                body_part.armor -= value
            else:
                body_part.health -= value
        return fab_damage
    return mast_damage


def knock_back(value):
    def mast_knock_back(master):
        def fab_knock_back(body_part):
            v = master.actual_hit.trace.v.normalized() * value
            body_part.master.master.push(v)
        return fab_knock_back
    return  mast_knock_back


def stun(value):
    def mast_stun(master):
        def fab_stun(value):
            pass
        return fab_stun
    return mast_stun