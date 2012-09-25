# -*- coding: utf-8 -*-
from sys import path
path.append('../')

from math import hypot, ceil,floor


from share.mathlib import *

from config import *

########################################################################

########################################################################

def intersec_point(A,B,C,D):
    "ищет точку пересечения двух векторов"
    vector = (B-A)
    if vector.y:
        div = vector.x.__truediv__(vector.y)
        divx = True
    elif vector.x:
        div = vector.y.__truediv__(vector.x)
        divx = False
    if C.x==D.x:
        x = C.x - A.x
        y = x/div if divx else x*div
        return A+ Point(x,y)
    elif C.y == D.y:
        y = C.y - A.y
        x = y*div if divx else y/div
        return A + Point(x,y)

def interception(A,B,C,D):
    "пересекаются ли отрезки"
    def ccw(A,B,C):
        return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def cross_tile(A, B, tilecord):
    "выдает соседние тайлы с которыми пересекается вектор и координаты пересечения"
    start = tilecord*TILESIZE
    null, CELL = 0 , TILESIZE
    cds = {tilecord + Point(0,1) : (start + Point(null ,CELL), start+Point(CELL,CELL)),
                tilecord + Point(1,0) : (start + Point(CELL, CELL), start + Point(CELL, null)),
                tilecord + Point(0,-1) : (start, start + Point(CELL, null)),
                tilecord + Point(-1,0) : (start, start + Point(null, CELL))}
    
    return [(ij, intersec_point(A,B,C, D)) for ij,(C, D) in cds.items() if interception(A,B,C,D)]
        

def get_cross(position, vector):
    "возвращает i,j пересекаемых векторов тайлов и координаты этих пересечений"
    end_cord = (position+vector)/TILESIZE #i,j конечнй точки
    results = []
    cur_tile = position/TILESIZE
    crossed = [cur_tile]
    while 1:
        counter = 0
        crossed_tiles = cross_tile(position, position+vector, cur_tile)
        #print 'loop', crossed_tiles, position, vector
        if crossed_tiles:
            for ij, cross in crossed_tiles:
                if not ij in crossed:
                    counter+=1
                    crossed.append(ij)
                    results.append((ij.get(), cross))
                    cur_tile = ij
                    if ij == end_cord:
                        return results
            if not counter:
                #print 'COUNTER BREAK'
                return results
        else:
            #print 'BREAK'
            return results
    return results


            
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
    #print interception(A,B,C,D)
    #6243:6085 117:106

    #position, vector = Point(6243,6085), Point(117,106)
    #print position, vector, position+ vector, position/TILESIZE, vector/TILESIZE, (position+ vector)/TILESIZE
    #print 'result', get_cross(position, vector)
    
    print rotate(Point(40, 0), 30)
    
    
