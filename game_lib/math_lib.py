# -*- coding: utf-8 -*-
from math import hypot, ceil,floor

from sys import path
path.append('../')
from config import TILESIZE

from config import *

########################################################################
def point_wrap(func):
    def wrap(self, point):
        if isinstance(point, Point):
            return func(self,point)
        else:
            raise TypeError("at %s  %s  isn't Point instance" % (func.__name__, str(point)))
    return wrap

def number_wrap(func):
    def wrap(self, number):
        if isinstance(number, (float,int,long)):
            return func(self,number)
        else:
            raise TypeError("at %s  %s  isn't number" % (func.__name__, str(number)))
    return wrap


    
class Point:
    "класс точек и векторов"
    def __init__(self,x,y):
        try:
            self.x = int(x)
            self.y = int(y)
        except TypeError:
            raise TypeError("%s %s not int or float" % (str(x),str(y)))
    def __nonzero__(self):
        return bool(self.x) or bool(self.y)
    @point_wrap
    def __eq__(self, point):
        return self.x==point.x and self.y==point.y
    @point_wrap
    def __lt__(self, point):
        "<"
        return abs(self)<abs(point)
    @point_wrap
    def __le__(self, point):
        "<="
        return abs(self)<=abs(point)
    @point_wrap
    def __gt__(self, point):
        ">"
        return abs(self)>abs(point)
    @point_wrap
    def __ge__(self, point):
        ">="
        return abs(self)>=abs(point)
    def __abs__(self):
        return hypot(self.x,self.y)
    @point_wrap
    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)
    @point_wrap
    def __sub__(self, point):
        "-"
        return Point(self.x - point.x, self.y - point.y)
    def __neg__(self):
        return Point(-self.x, -self.y)
    @number_wrap
    def __mul__(self, number):
        '*'
        return Point(self.x*number, self.y*number)
    @number_wrap
    def __div__(self, number):
        return Point(round(self.x/number), round(self.y/number))
    @number_wrap
    def __truediv__(self, number):
        return Point(round(self.x/number), round(self.y/number))
    def get(self):
        return (self.x, self.y)
    def __repr__(self):
        return "%s:%s" % self.get()
    def __hash__(self):
        return hash((self.x, self.y))
        
NullPoint = Point(0,0)

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
    
    
