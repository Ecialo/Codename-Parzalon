import cocos.euclid as eu

class Geometry(eu.Geometry):

    def _intersect_unimplemented(self, other):
        super(Geometry, self)._intersect_unimplemented(other)
        
    def _connect_unimplemented(self, other):
        super(Geometry, self)._connect_unimplemented(other)

    def __ne__(self, other): #Pavgran: implemented
        return not self.__eq__(other)
    
    _intersect_rectangle = _intersect_unimplemented
    _connect_rectangle = _connect_unimplemented
    
def _intersect_point2_rectangle(P, R):
    if R.p.x <= P.x <= R.p.x + R.v.x and\
       R.p.y <= P.y <= R.p.y + R.v.y:
           return P.copy()
    else:
        return None
    
def _intersect_line2_rectangle(L, R): #Pavgran: reworked
    l_line = Line2(R.plb, R.plt)
    r_line = Line2(R.prb, R.prt)
    t_line = Line2(R.plt, R.prt)
    b_line = Line2(R.plb, R.prb)
    l_int = L.intersect(l_line)
    r_int = L.intersect(r_line)
    t_int = L.intersect(t_line)
    b_int = L.intersect(b_line)
    if isinstance(l_int, Line2) or isinstance(r_int, Line2):
        return LineSegment2(b_int, t_int)
    if isinstance(b_int, Line2) or isinstance(t_int, Line2):
        return LineSegment2(l_int, r_int)
    l_int_in = _intersect_point2_rectangle(l_int, R)\
               if l_int is not None else None
    r_int_in = _intersect_point2_rectangle(r_int, R)\
               if r_int is not None else None
    t_int_in = _intersect_point2_rectangle(t_int, R)\
               if t_int is not None else None
    b_int_in = _intersect_point2_rectangle(b_int, R)\
               if b_int is not None else None
    res = filter(lambda x: x is not None,\
                 [l_int_in, r_int_in, t_int_in, b_int_in])
    if len(res) == 0:
        return None
    elif res[0] == res[1]:
        return res[0]
    else:
        return LineSegment2(res[0], res[1])

def _intersect_linesegment2_rectangle(L, R): #Pavgran: implemented
    p1 = L.p1
    p2 = L.p2
    p1_in = _intersect_point2_rectangle(p1, R)
    p2_in = _intersect_point2_rectangle(p2, R)
    res = filter(lambda x: x is not None, [p1_in, p2_in])
    if len(res) == 0:
        if p1.x < R.p.x and p2.x < R.p.x or\
           p1.x > R.p.x + R.v.x and p2.x > R.p.x + R.v.x or\
           p1.y < R.p.y and p2.y < R.p.y or\
           p1.y > R.p.y + R.v.y and p2.y > R.p.y + R.v.y:
            return None
        else:
            L = Line2(L.p, L.v)
            return L.intersect(R)
    elif len(res) == 2:
        return LineSegment2(p1_in, p2_in)
    else:
        if p1_in is not None:
            p3 = p2
        else:
            p3 = p1
        if p3.x < R.p.x:
            p3.y += (p1.y - p2.y) * (R.p.x - p3.x) / (p1.x - p2.x)
            p3.x = R.p.x
        elif p3.x > R.p.x + R.v.x:
            p3.y += (p1.y - p2.y) * (R.p.x + R.v.x - p3.x) / (p1.x - p2.x)
            p3.x = R.p.x + R.v.x
        if p3.y < R.p.y:
            p3.x += (p1.x - p2.x) * (R.p.y - p3.y) / (p1.y - p2.y)
            p3.y = R.p.y
        elif p3.y > R.p.y + R.v.y:
            p3.x += (p1.x - p2.x) * (R.p.y + R.v.y - p3.y) / (p1.y - p2.y)
            p3.y = R.p.y + R.v.y
        if p3 == res[0]:
            return p3
        else:
            return LineSegment2(p3, res[0])

def _intersect_circle_rectangle(C, R):
    pass

def _intersect_rectangle_rectangle(A, B): #Pavgran: implemented
    lba_inb = _intersect_point2_rectangle(A.plb, B)
    rtb_ina = _intersect_point2_rectangle(B.prt, A)
    if lba_inb is not None and rtb_ina is not None: #A: 1 in B, B: 1 in A
        if lba_inb.x < rtb_ina.x and lba_inb.y < rtb_ina.y:
            return Rectangle(lba_inb, rtb_ina)
        elif lba_inb.x == rtb_ina.x and lba_inb.y == rtb_ina.y:
            return lba_inb.copy()
        else:
            return LineSegment2(lba_inb, rtb_ina)    
    rta_inb = _intersect_point2_rectangle(A.prt, B)
    lbb_ina = _intersect_point2_rectangle(B.plb, A)
    if rta_inb is not None and lbb_ina is not None: #A: 1 in B, B: 1 in A
        if lbb_ina.x < rta_inb.x and lbb_ina.y < rta_inb.y:
            return Rectangle(lbb_ina, rta_inb)
        elif lbb_ina.x == rta_inb.x and lbb_ina.y == rta_inb.y:
            return lbb_ina.copy()
        else:
            return LineSegment2(lbb_ina, rta_inb)
    if lba_inb is not None and rta_inb is not None: #A: 4 in B, B: 0 in A
        return A.copy()
    if lbb_ina is not None and rtb_ina is not None: #A: 0 in B, B: 4 in A
        return B.copy()
    lta_inb = _intersect_point2_rectangle(A.plt, B)
    rbb_ina = _intersect_point2_rectangle(B.prb, A)
    if lta_inb is not None and rbb_ina is not None: #A: 1 in B, B: 1 in A
        if lta_inb.x < rbb_ina.x and lta_inb.y > rbb_ina.y:
            return Rectangle((lta_inb.x, rbb_ina.y),\
                             (rbb_ina.x, lta_inb.y))
        elif lta_inb.x == rbb_ina.x and lta_inb.y == rbb_ina.y:
            return lta_inb.copy()
        else:
            return LineSegment2(lta_inb, rbb_ina)
    if lba_inb is not None and lta_inb is not None: #A: 2 in B, B: 0 in A
        if lba_inb.x < B.prt.x:
            return Rectangle(lba_inb, (B.prt.x, lta_inb.y))
        else:
            return LineSegment2(lba_inb, lta_inb)
    if rtb_ina is not None and rbb_ina is not None: #A: 0 in B, B: 2 in A
        if A.plb.x < rtb_ina.x:
            return Rectangle((A.plb.x, rbb_ina.y), rtb_ina)
        else:
            return LineSegment2(rbb_ina, rtb_ina)
    if lta_inb is not None and rta_inb is not None: #A: 2 in B, B: 0 in A
        if B.plb.y < lta_inb.y:
            return Rectangle((lta_inb.x, B.plb.y), rta_inb)
        else:
            return LineSegment2(lta_inb, rta_inb)
    if lbb_ina is not None and rbb_ina is not None: #A: 0 in B, B: 2 in A
        if lbb_ina.y < A.prt.y:
            return Rectangle(lbb_ina, (rbb_ina.x, A.prt.y))
        else:
            return LineSegment2(lbb_ina, rbb_ina)
    rba_inb = _intersect_point2_rectangle(A.prb, B)
    ltb_ina = _intersect_point2_rectangle(B.plt, A)
    if rba_inb is not None and ltb_ina is not None: #A: 1 in B, B: 1 in A
        if ltb_ina.x < rba_inb.x and ltb_ina.y > rba_inb.y:
            return Rectangle((ltb_ina.x, rba_inb.y),\
                             (rba_inb.x, ltb_ina.y))
        elif ltb_ina.x == rba_inb.x and ltb_ina.y == rba_inb.y:
            return ltb_ina.copy()
        else:
            return LineSegment2(rba_inb, ltb_ina)
    if rta_inb is not None and rba_inb is not None: #A: 2 in B, B: 0 in A
        if B.plb.x < rta_inb.x:
            return Rectangle((B.plb.x, rba_inb.y), rta_inb)
        else:
            return LineSegment2(rba_inb, rta_inb)
    if lbb_ina is not None and ltb_ina is not None: #A: 0 in B, B: 2 in A
        if lbb_ina.x < A.prt.x:
            return Rectangle(lbb_ina, (A.prt.x, ltb_ina.y))
        else:
            return LineSegment2(lbb_ina, ltb_ina)
    if lba_inb is not None and rba_inb is not None: #A: 2 in B, B: 0 in A
        if lba_inb.y < B.prt.y:
            return Rectangle(lba_inb, (rba_inb.x, B.prt.y))
        else:
            return LineSegment2(lba_inb, rba_inb)
    if ltb_ina is not None and rtb_ina is not None: #A: 0 in B, B: 2 in A
        if A.plb.y < ltb_ina.y:
            return Rectangle((ltb_ina.x, A.plb.y), rtb_ina)
        else:
            return LineSegment2(ltb_ina, rtb_ina)
    

def _connect_point2_rectangle(P, R):
    pass

def _connect_line2_rectangle(L, R):
    pass

def _connect_circle_rectangle(C, R):
    pass

def _connect_rectangle_rectangle(A, B):
    pass



def _set_lb(self, other): #Pavgran: added parameter checking
    if not isinstance(other, Point2):
        other = Point2(*other)
    self.p = other.copy()

def _set_rb(self, other): #Pavgran: added parameter checking
    if not isinstance(other, Point2):
        other = Point2(*other)
    self.p = other - eu.Vector2(self.v.x, 0.0)

def _set_lt(self, other): #Pavgran: added parameter checking
    if not isinstance(other, Point2):
        other = Point2(*other)
    self.p = other - eu.Vector2(0.0, self.v.y)

def _set_rt(self, other): #Pavgran: added parameter checking
    if not isinstance(other, Point2):
        other = Point2(*other)
    self.p = other - eu.Vector2(self.v.x, self.v.y)

def _set_c(self, other): #Pavgran: added parameter checking
    if not isinstance(other, Point2):
        other = Point2(*other)
    self.p = other - eu.Vector2(self.v.x, self.v.y)/2



class Rectangle(Geometry):
    
    __slots__ = ['p', 'v']

    def __init__(self, st, en): #Pavgran: added parameter checking
        if not isinstance(st, eu.Point2):
            assert hasattr(st, '__len__') and len(st) == 2
            st = Point2(*st)
        if not isinstance(en, eu.Point2) and not isinstance(en, eu.Vector2):
            assert hasattr(en, '__len__') and len(en) == 2
            en = Point2(*en)
        if isinstance(en, eu.Point2):
            self.v = en-st
            if self.v.y == 0 or self.v.x == 0:
                raise AttributeError, 'Zero square rect'
        else:
            if en.y == 0 or en.x == 0:
                raise AttributeError, 'Zero square rect'
            self.v = en.copy()
        self.p = st.copy()
        if self.v.x < 0:
            self.p.x += self.v.x
            self.v.x = -self.v.x
        if self.v.y < 0:
            self.p.y += self.v.y
            self.v.y = -self.v.y
            
    plb = property(lambda self: self.p.copy(), _set_lb)
    plt = property(lambda self: self.plb + eu.Vector2(0, self.v.y), _set_lt)
    prt = property(lambda self: self.plb + self.v, _set_rt)
    prb = property(lambda self: self.plb + eu.Vector2(self.v.x, 0), _set_rb)
    pc = property(lambda self: self.plb + self.v/2, _set_c)
    h_height = property(lambda self: self.v.y/2)
    h_width = property(lambda self: self.v.x/2)


    def __copy__(self):
        return self.__class__(self.p, self.v)
    
    copy = __copy__
    
    def __repr__(self):
        plb = self.plb
        prt = self.prt
        return 'Rectangle(<%.2f, %.2f>, <%.2f, %.2f>, <%.2f, %.2f>, <%.2f, %.2f>)' % \
            (plb.x, plb.y, plb.x, prt.y,
             prt.x, prt.y, prt.x, plb.y)

    def __eq__(self, other): #Pavgran: implemented
        if isinstance(other, Rectangle):
            return self.p == other.p and self.v == other.v
        else:
            return False
        
    def intersect(self, other):
        return other._intersect_rectangle(self)
    
    def _intersect_point2(self, other):
        return _intersect_point2_rectangle(other, self)
    
    def _intersect_line2(self, other):
        return _intersect_line2_rectangle(other, self)
    
    def _intersect_circle(self, other):
        return _intersect_circle_rectangle(other, self)
    
    def _intersect_rectangle(self, other):
        return _intersect_rectangle_rectangle(other, self)
    
    def connect(self, other):
        return other._connect_rectangle(other, self)
    
    def _connect_point2(self, other):
        return _connect_point2_rectangle(other, self)
    
    def _connect_line2(self, other):
        return _connect_line2_rectangle(other, self)
    
    def _connect_circle(self, other):
        return _connect_circle_rectangle(other, self)
    
    def _connect_rectangle(self, other):
        return _connect_rectangle_rectangle(other, self)



class Circle(Geometry, eu.Circle):
    
    def _intersect_rectangle(self, other):
        return _intersect_circle_rectangle(self, other)
    
    def _connect_rectangle(self, other):
        return _connect_circle_rectangle(self, other)

class Point2(Geometry, eu.Point2):
    
    def _intersect_rectangle(self, other):
        return _intersect_point2_rectangle(self, other)
    
    def _connect_rectangle(self, other):
        return _connect_point2_rectangle(self, other)

class Line2(Geometry, eu.Line2):
    
    def _intersect_rectangle(self, other):
        return _intersect_line2_rectangle(self, other)
    
    def _connect_rectangle(self, other):
        return _connect_line2_rectangle(self, other)

class Ray2(Line2, eu.Ray2):
    
    pass

class LineSegment2(Line2, eu.LineSegment2):
    
    def __eq__(self, other): #Pavgran: implemented
        if isinstance(other, LineSegment2):
            p1 = self.p1
            p2 = self.p2
            p3 = other.p1
            p4 = other.p2
            return p1 == p3 and p2 == p4 or p1 == p4 and p2 == p3
        else:
            return False

    def _intersect_rectangle(self, other): #Pavgran: implemented
        return _intersect_linesegment2_rectangle(self, other)
