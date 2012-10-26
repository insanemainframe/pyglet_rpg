#!/usr/bin/env python
# -*- coding: utf-8 -*-
cdef dict cds

from share.mathlib cimport Point

from math import hypot, ceil
from collections import namedtuple

from config import *



def intersec_point(Point A,Point B,Point C,Point D):
    "ищет точку пересечения двух векторов"
    cdef Point vector
    cdef float div, divx, divy, x,y

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

def interception(Point A,Point B,Point C,Point D):
    "пересекаются ли отрезки"
    def ccw(Point A,Point B,Point C):
        return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)




def cross_tile(Point A, Point B, Point tilecord):
    "выдает соседние тайлы с которыми пересекается вектор и координаты пересечения"
    cdef Point  start, ij
    cdef int null, CELL

    start = tilecord*TILESIZE
    null, CELL = 0 , TILESIZE
    
    cds = {tilecord + Point(0,1) : (start + Point(null ,CELL), start+Point(CELL,CELL)),
                tilecord + Point(1,0) : (start + Point(CELL, CELL), start + Point(CELL, null)),
                tilecord + Point(0,-1) : (start, start + Point(CELL, null)),
                tilecord + Point(-1,0) : (start, start + Point(null, CELL))}
    
    return ((ij, intersec_point(A,B,C, D)) for ij,(C, D) in cds.items() if interception(A,B,C,D))


    

def get_cross(Point position, Point vector):
    "возвращает i,j пересекаемых векторов тайлов и координаты этих пересечений"
    cdef Point end_cord, ij, cross

    end_cord = (position+vector)/TILESIZE #i,j конечнй точки
    
    for ij, cross in cross_tile(position, position+vector, position/TILESIZE):
        yield (ij.get(), cross)
        if ij == end_cord:
            break
    raise StopIteration




#####################################################################

cross_tuple = namedtuple('cross_tuple', ['point', 'cord', 'dist'])

def round_cord(cord, Ceil = False):
    cord = cord/TILESIZE
    if Ceil:
        cord = ceil(float(cord))
        cord = int(cord)

    else:
        cord = int(float(cord))

    return cord*TILESIZE



def get_interception_point(p1, p2, p3, p4):
    x1, x2, x3, x4 = p1.x, p2.x, p3.x, p4.x
    y1, y2, y3, y4 = p1.y, p2.y, p3.y, p4.y

    not_par = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if not_par:    
        x_numerator = (x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)
        x_denumerator = (x1-x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        y_numerator = (x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)
        y_denumerator = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)

        x = x_numerator/x_denumerator
        y = y_numerator/y_denumerator

        return Point(x,y)
    else:
        return False


def walk_by_cord(c1, c2, start, end, cord):
    if c1>c2:
        crange = range(c2, c1+TILESIZE, TILESIZE)
    else:
        crange = range(c1, c2 +TILESIZE, TILESIZE)
    if cord=='x':
        point = lambda c, two: Point(c, two.y+1)
        cord = lambda x, ipoint: (c/TILESIZE, ipoint.y/TILESIZE)
    else:
        point = lambda c, two: Point(two.x+1, c)
        cord = lambda x, ipoint: (ipoint.x/TILESIZE, c/TILESIZE)

    for c in crange:
        s = point(c, start)
        e = point(c, end)
        i_point =  get_interception_point(start, end, s, e)
        if i_point:
            dist = abs(i_point - start)
            yield cross_tuple(i_point, cord(c, i_point), dist)



def new_get_cross(start, vector):
    end = start + vector

    if start.x == end.x:
        vector = Point(vector.x+1, vector.y)
        end = start + vector
    if start.y == end.y:
        vector = Point(vector.x, vector.y+1)
        end = start + vector

    x1 = round_cord(start.x)
    x2 = round_cord(end.x)

    y1 = round_cord(start.y)
    y2 = round_cord(end.y)

    xlist = list(walk_by_cord(x1, x2, start, end, 'x')) #[1:]
    ylist = list(walk_by_cord(y1, y2, start, end, 'y')) #[1:]


    crossed = ylist + xlist

    #print [cross.cord for cross in crossed]
    crossed.sort(key = lambda cross: cross.dist)


    for cross in crossed:
        yield cross.cord, cross.point
