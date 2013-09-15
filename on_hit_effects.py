__author__ = 'Ecialo'

def fab_damage(value):
    def mast_damage(master):
        def damage(body_part):
            if body_part.armor > value:
                body_part.armor -= value
            else:
                body_part.health -= value
            print body_part.__class__
        return damage
    return mast_damage