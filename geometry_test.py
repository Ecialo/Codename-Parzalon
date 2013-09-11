# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import unittest
import geometry as g
from cocos import euclid as eu

class  Geometry_Rectangle_test(unittest.TestCase):
    #def setUp(self):
    #       pass

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None
    def test_set_up(self):
        stp = (0.0, 0.0)
        nlbc = (1.0, 1.0)
        nrbc = (2.0, 1.0)
        nrtc = (2.0, 2.0)
        nltc = (1.0, 2.0)
        
        vec = eu.Vector2(1.0, 1.0)
        rec_point = g.Point2(0.0, 0.0)
        rect = g.Rectangle(rec_point, vec)
        oth_rect = g.Rectangle(stp, nlbc)
        
        et = g.Rectangle(g.Point2(*nlbc), vec)
        
        rect.plb = g.Point2(*nlbc)
        oth_rect.plb = nlbc
        self.assertEquals(rect, et)
        self.assertEquals(oth_rect, et)
        
        rect.plt = g.Point2(*nltc)
        oth_rect.plt = nltc
        self.assertEquals(rect, et)
        self.assertEquals(oth_rect, et)
        
        rect.prb = g.Point2(*nrbc)
        oth_rect.prb = nrbc
        self.assertEquals(rect, et)
        self.assertEquals(oth_rect, et)
        
        rect.prt = g.Point2(*nrtc)
        oth_rect.prt = nrtc
        self.assertEquals(rect, et)
        self.assertEquals(oth_rect, et)
        
        
    def test_rectangle_point(self):
        vec = eu.Vector2(1.0, 1.0)
        lb_st_p = g.Point2(0.0, 0.0)
        p_in = g.Point2(0.5, 0.5)
        p_out = g.Point2(2.0, 2.0)
        p_edge = g.Point2(0.5, 0.0)
        p_cor = g.Point2(1.0, 1.0)
        rect = g.Rectangle(lb_st_p, vec)
        intr_in = rect.intersect(p_in)
        intr_out = rect.intersect(p_out)
        intr_edge = rect.intersect(p_edge)
        intr_cor = rect.intersect(p_cor)
        self.assertEquals(intr_in, p_in, msg = "Point inside")
        self.assertIs(intr_out, None, msg = "Point outside")
        self.assertEquals(intr_edge, p_edge, msg = "Point on edge")
        self.assertEquals(intr_cor, p_cor, msg = "Point on corner")

    def test_rectangle_rectangle_corners(self):
        vec = eu.Vector2(1.0, 1.0)
        hvec = vec/2
        lb_st_p = g.Point2(0.0, 0.0)
        rb_st_p = g.Point2(1.0, 0.0)
        lt_st_p = g.Point2(0.0, 1.0)
        rt_st_p = g.Point2(1.0, 1.0)
        c_st_p = g.Point2(0.5, 0.5)
        rectangle_lb = g.Rectangle(lb_st_p, vec)
        rectangle_rb = g.Rectangle(rb_st_p, vec)
        rectangle_lt = g.Rectangle(lt_st_p, vec)
        rectangle_rt = g.Rectangle(rt_st_p, vec)
        rectangle_c = g.Rectangle(c_st_p, vec)
        lb_intr = rectangle_lb.intersect(rectangle_c) 
        rb_intr = rectangle_rb.intersect(rectangle_c)
        lt_intr = rectangle_lt.intersect(rectangle_c)
        rt_intr = rectangle_rt.intersect(rectangle_c)
        r_c_intr = rectangle_rt.intersect(rectangle_lb)
        l_c_intr = rectangle_rb.intersect(rectangle_lt)
        self.assertEquals(lb_intr, g.Rectangle(g.Point2(0.5, 0.5), hvec), 
                          msg = "Left_bot_Center")
        self.assertEquals(rb_intr, g.Rectangle(g.Point2(1.0, 0.5), hvec), 
                          msg = "Right_bot_Center")
        self.assertEquals(lt_intr, g.Rectangle(g.Point2(0.5, 1.0), hvec), 
                          msg = "Left_top_Center")
        self.assertEquals(rt_intr, g.Rectangle(g.Point2(1.0, 1.0), hvec), 
                          msg = "Right_top_Center")
        self.assertEquals(r_c_intr, g.Point2(1.0, 1.0), 
                          msg = "Rigth_top_corner_Left_bot_corner")
        self.assertEquals(l_c_intr, g.Point2(1.0, 1.0), 
                          msg = "Right_bot_corner_Left_top_corner")
        
    def test_rectangle_rectangle_side(self):
        vec = eu.Vector2(1.0, 1.0)
        lb_st_p = g.Point2(0.0, 0.0)
        lt_st_p = g.Point2(0.0, 1.0)
        rt_st_p = g.Point2(1.0, 1.0)
        htb_st_p = g.Point2(0.0, 0.5)
        hlr_st_p = g.Point2(0.5, 1.0)
        r_lb = g.Rectangle(lb_st_p, vec)
        r_lt = g.Rectangle(lt_st_p, vec)
        r_rt = g.Rectangle(rt_st_p, vec)
        r_htb = g.Rectangle(htb_st_p, vec)
        r_hlr = g.Rectangle(hlr_st_p, vec)
        top_intr = r_lb.intersect(r_lt)
        bot_intr = r_lt.intersect(r_lb)
        left_intr = r_rt.intersect(r_lt)
        right_intr = r_lt.intersect(r_rt)
        ht_intr = r_lb.intersect(r_htb)
        hb_intr = r_lt.intersect(r_htb)
        hl_intr = r_rt.intersect(r_hlr)
        hr_intr = r_lt.intersect(r_hlr)
        self.assertEquals(top_intr, g.LineSegment2(g.Point2(0.0, 1.0), 
                                                   g.Point2(1.0, 1.0)),
                          msg = "Top_edge")
        self.assertEquals(bot_intr, g.LineSegment2(g.Point2(1.0, 1.0), 
                                                   g.Point2(0.0, 1.0)),
                          msg = "Bot_edge")
        self.assertEquals(left_intr, g.LineSegment2(g.Point2(1.0, 2.0), 
                                                    g.Point2(1.0, 1.0)),
                          msg = "Left_edge")
        self.assertEquals(right_intr, g.LineSegment2(g.Point2(1.0, 1.0), 
                                                    g.Point2(1.0, 2.0)),
                          msg = "Right_edge")
        self.assertEquals(ht_intr, g.Rectangle(g.Point2(0.0, 0.5),
                                               g.Point2(1.0, 1.0)),
                          msg = "Top side")
        self.assertEquals(hb_intr, g.Rectangle(g.Point2(0.0, 1.0),
                                               g.Point2(1.0, 1.5)),
                          msg = "Bot side")
        self.assertEquals(hl_intr, g.Rectangle(g.Point2(1.0, 1.0),
                                               g.Point2(1.5, 2.0)),
                          msg = "Left side")
        self.assertEquals(hr_intr, g.Rectangle(g.Point2(0.5, 1.0),
                                               g.Point2(1.0, 2.0)),
                          msg = "Right side")
        
    
    def test_rectangle_rectangle_inside(self):
        vec = eu.Vector2(3.0, 3.0)
        vec_s = eu.Vector2(1.0, 1.0)
        lb_st_p = g.Point2(0.0, 0.0)
        rt_st_p = g.Point2(1.0, 1.0)
        rectangle_lb = g.Rectangle(lb_st_p, vec)
        rectangle_rt = g.Rectangle(rt_st_p, vec_s)
        rect_inside = rectangle_lb.intersect(rectangle_rt)
        rect_inside2 = rectangle_rt.intersect(rectangle_lb)
        self.assertEquals(rect_inside, rectangle_rt)
        self.assertEquals(rect_inside2, rectangle_rt)
    
    def test_rectangle_rectangle_none(self):
        vec = eu.Vector2(1.0, 1.0)
        lb_st_p = g.Point2(0.0, 0.0)
        rb_st_p = g.Point2(2.0, 0.0)
        rectangle1 = g.Rectangle(lb_st_p, vec)
        rectangle2 = g.Rectangle(rb_st_p, vec)
        intr1 = rectangle1.intersect(rectangle2)
        intr2 = rectangle2.intersect(rectangle1)
        self.assertIs(intr1, None)
        self.assertIs(intr2, None)
    
    def test_rectangle_line_cross(self):
        vec = eu.Vector2(1.0, 1.0)
        ovec = eu.Vector2(1.0, -1.0)
        hvec = vec/2
        ohvec = ovec/2
        rec_point = g.Point2(0.5, 0.5)
        rect = g.Rectangle(rec_point, vec)
        tlc_l = g.Line2(g.Point2(0.0, 1.0), vec)# eu.Vector2(1.0, 1.0))
        tle_l = g.Line2(g.Point2(0.0, 0.5), vec)# eu.Vector2(1.5, 1.5))
        cl_l = g.Line2(g.Point2(0.0, 0.0), vec)# eu.Vector2(2.0, 2.0))
        bre_l = g.Line2(g.Point2(0.5, 0.0), vec)# eu.Vector2(1.5, 1.5))
        brc_l = g.Line2(g.Point2(1.0, 0.0), vec)# eu.Vector2(1.0, 1.0))
        trc_l = g.Line2(g.Point2(1.0, 2.0), ovec)# eu.Vector2(1.0, -1.0))
        tre_l = g.Line2(g.Point2(0.5, 2.0), ovec)# eu.Vector2(1.5, -1.5))
        cr_l = g.Line2(g.Point2(0.0, 2.0), ovec)# eu.Vector2(2.0, -2.0))
        ble_l = g.Line2(g.Point2(0.0, 1.5), ovec)# eu.Vector2(1.5, -1.5))
        blc_l = g.Line2(g.Point2(0.0, 1.0), ovec)# eu.Vector2(1.0, -1.0))
        tlc_intr = rect.intersect(tlc_l)
        tle_intr = rect.intersect(tle_l)
        cl_intr = rect.intersect(cl_l)
        bre_intr = rect.intersect(bre_l)
        brc_intr = rect.intersect(brc_l)
        trc_intr = rect.intersect(trc_l)
        tre_intr = rect.intersect(tre_l)
        cr_intr = rect.intersect(cr_l)
        ble_intr = rect.intersect(ble_l)
        blc_intr = rect.intersect(blc_l)
        self.assertEqual(tlc_intr, rect.plt, 
                         msg = "Left_top_corner")
        self.assertEqual(tle_intr, g.LineSegment2(g.Point2(0.5, 1), hvec), 
                         msg = "Left to top")
        self.assertEqual(cl_intr, g.LineSegment2(rect.plb, rect.prt), 
                         msg = "Left_bot_corner to right_top_corner")
        self.assertEqual(bre_intr, g.LineSegment2(g.Point2(1.0, 0.5), hvec), 
                         msg = "Bot to right")
        self.assertEqual(brc_intr, rect.prb, 
                         msg = "Right_bot_corner")
        self.assertEqual(trc_intr, rect.prt, 
                         msg = "Right_top_corner")
        self.assertEqual(tre_intr, g.LineSegment2(g.Point2(1.0, 1.5), ohvec), 
                         msg = "Top to right")
        self.assertEqual(cr_intr, g.LineSegment2(rect.plt, rect.prb), 
                         msg = "Left_top_corner to right_bot_corner")
        self.assertEqual(ble_intr, g.LineSegment2(g.Point2(0.5, 1.0), ohvec), 
                         msg = "Left to bot")
        self.assertEqual(blc_intr, rect.plb, 
                         msg = "Left_bot_corner")
    
    def test_rectangle_line_parallel(self):
        vec = eu.Vector2(1.0, 1.0)
        rec_point = g.Point2(0.0, 0.0)
        rect = g.Rectangle(rec_point, vec)
        hor_l = g.Line2(g.Point2(0.0, 0.5), eu.Vector2(1.0, 0.0))
        ver_l = g.Line2(g.Point2(0.5, 0.0), eu.Vector2(0.0, 1.0))
        hor_intr = rect.intersect(hor_l)
        ver_intr = rect.intersect(ver_l)
        self.assertEqual(hor_intr, g.LineSegment2(g.Point2(0.0, 0.5), 
                                                  g.Point2(1.0, 0.5)))
        self.assertEqual(ver_intr, g.LineSegment2(g.Point2(0.5, 0.0),
                                                  g.Point2(0.5, 1.0)))
                                                  
    def test_rectangle_line_in(self):
        vec = eu.Vector2(3.0, 3.0)
        rec_point = g.Point2(0.0, 0.0)
        rect = g.Rectangle(rec_point, vec)
        lsg = g.LineSegment2(g.Point2(1.0, 1.0), eu.Vector2(1.0, 0.0))
        intr = rect.intersect(lsg)
        self.assertEquals(intr, lsg)
        
    def test_rectangle_line_half_in(self):
        vec = eu.Vector2(2.0, 2.0)
        rec_point = g.Point2(1.0, 0.0)
        rect = g.Rectangle(rec_point, vec)
        lsg = g.LineSegment2(g.Point2(0.0, 1.0), eu.Vector2(2.0, 0.0))
        intr = rect.intersect(lsg)
        self.assertEquals(intr, g.LineSegment2(g.Point2(1.0, 1.0), 
                                               eu.Vector2(1.0, 0.0)))
    
    def test_rectangle_line_none(self):
        vec = eu.Vector2(1.0, 1.0)
        rec_point = g.Point2(0.0, 0.0)
        line_point = g.Point2(5.0, 5.0)
        l_vec_v = eu.Vector2(0.0, 1.0)
        l_vec_h = eu.Vector2(1.0, 0.0)
        l_v = g.Line2(line_point, l_vec_v)
        l_h = g.Line2(line_point, l_vec_h)
        rec = g.Rectangle(rec_point, vec)
        intrv = rec.intersect(l_v)
        intrh = rec.intersect(l_h)
        self.assertIs(intrv, None, msg = "Horizontal")
        self.assertIs(intrh, None, msg = "Vertical")

if __name__ == '__main__':
    unittest.main()

