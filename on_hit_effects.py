__author__ = 'Ecialo'

def fab_damage(value):
    def mast_damage(master):
        def damage(body_part):
            if body_part.armor > value:
                body_part.armor -= value
            else:
                body_part.health -= value
        return damage
    return mast_damage