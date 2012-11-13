# -*- coding: utf-8 -*-
from math import hypot


from share.mathlib import *

from config import *
from share.logger import print_log


########################################################################
from random import random

def chance(n):
    n = n/100.0
    if random()<n:
        return True
    else:
        return False



            
########################################################################
from math import sin ,tan, radians

def rotate(AB, angle):
    angle = radians(angle)
    CB_len = tan(angle)*abs(AB)
    #
    x = -AB.y
    y = AB.x
    CB_direct = Point(x,y)
    CB = CB_direct * (CB_len/abs(AB))
    #
    AC = AB + CB
    AD = AB*(abs(AB)/abs(AC))
    return AD
    


########################################################################
if __name__=='__main__':
    #A,B,C,D = Point(2,2), Point(5,6), Point(0,0), Point(4,0)
    #print_log interception(A,B,C,D)
    #6243:6085 117:106

    #position, vector = Point(6243,6085), Point(117,106)
    #print_log position, vector, position+ vector, position/TILESIZE, vector/TILESIZE, (position+ vector)/TILESIZE
    #print_log 'result', get_cross(position, vector)
    
    print_log(rotate(Point(40, 0), 30))
    
    
