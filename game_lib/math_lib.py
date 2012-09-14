# -*- coding: utf-8 -*-
from math import hypot, ceil,floor

from sys import path
path.append('../')
from config import TILESIZE

class Point:
    "класс точек и векторов"
    def __init__(self,x=0,y=0):
        try:
            self.x = int(x)
            self.y = int(y)
        except TypeError:
            raise TypeError("%s %s not int or float" % (str(x),str(y)))
    def __nonzero__(self):
        if self.x or self.y:
            return True
        else:
            return False
            
    def __eq__(self, point):
        if isinstance(point, Point):
            return self.x==point.x and self.y==point.y
        else:
            raise TypeError(" __eq__ %s  isn't Point instance" % str(point))
    def __lt__(self, point):
        "<"
        if isinstance(point, Point):
            return abs(self)<abs(point)
        else:
            raise TypeError("__lt__ %s point isn't Point instance" % str(point))
    def __le__(self, point):
        "<="
        if isinstance(point, Point):
            return abs(self)<=abs(point)
        else:
            raise TypeError("__le__ %s point isn't Point instance" % str(point))
    def __gt__(self, point):
        ">"
        if isinstance(point, Point):
            return abs(self)>abs(point)
        else:
            raise TypeError("__gt__ %s point isn't Point instance" % str(point))
    def __ge__(self, point):
        ">="
        if isinstance(point, Point):
            return abs(self)>=abs(point)
        else:
            raise TypeError("__ge__ %s point isn't Point instance" % str(point))
    def __abs__(self):
        return hypot(self.x,self.y)
    def __add__(self, point):
        if isinstance(point, Point):
            return Point(self.x + point.x, self.y + point.y)
        else:
            raise TypeError("__add__ %s point isn't Point instance" % str(point))
    def __sub__(self, point):
        "-"
        if isinstance(point, Point):
            return Point(self.x - point.x, self.y - point.y)
        else:
            raise TypeError("__sub__ %s point isn't Point instance" % str(point))
    def __neg__(self):
        return Point(-self.x, -self.y)
    def __mul__(self, number):
        return Point(self.x*number, self.y*number)
    def __div__(self, number):
        return Point(round(self.x/number), round(self.y/number))
    def __truediv__(self, number):
        return Point(round(self.x/number), round(self.y/number))
    def get(self):
        return (self.x, self.y)
    def round(self):
        return Point(int(self.x), int(self.y))
    def __repr__(self):
        return "%s:%s" % self.get()
    def __hash__(self):
        return hash((self.x, self.y))
        
def roundup(x):
    if x>=0:
        return ceil(x)
    else:
        return floor(x)

def get_cross(position, vector):
    single_move = vector*(TILESIZE/abs(vector))
    new_position = position + single_move
    if new_position/TILESIZE == position/TILESIZE:
        new_position = position + single_move*1.5
    i,j = (new_position/TILESIZE).get()
    return i,j



