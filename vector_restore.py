from cocos import euclid as eu
from math import sqrt

def restore_vector(v1, length, cos):
    '''This come from resoluttion system
    bx^2 + by^2 = ch2^2
    ax*bx + ay*by = ch1 * ch2 *cos
    Where ax, ay params of knowed vector
          bx, by params of required vector
          ch1 length of knowed vector
          ch2 length of required vector'''
    ax, ay = v1.x, v1.y
    if ax == 0:
        return eu.Vector2(0.0, 1.0) * length
    if ay == 0:
        return eu.Vector2(1.0, 0.0) * length
    ch1, ch2 = abs(v1), length
    C = ch1*ch2*cos/ax
    k = ay/ax
    D = 4*C*C*k*k - 4*(1+k*k)*(C - ch2*ch2)
    m = C*k/(1 + k*k)
    d = sqrt(D)/(2*(1 + k*k))
    by1, by2 = m + d, m - d
    bx1, bx2 = C - by1*k, C - by2 * k
    f_1h = bx1 < 0
    f_1v = by1 < 0
    if ax > 0:
        if f_1h:
            return eu.Vector2(bx1, by1)
        else:
            return eu.Vector2(bx2, by2)
    elif ax < 0:
        if f_1h:
            return eu.Vector2(bx2, by2)
        else:
            return eu.Vector2(bx1, by1)
        
    
