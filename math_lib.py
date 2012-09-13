# -*- coding: utf-8 -*-
from math import hypot, ceil,floor
from config import TILESIZE

class Point:
    def __init__(self,x=0,y=0):
        try:
            self.x = int(x)
            self.y = int(y)
        except TypeError:
            print x,y
            raise TypeError
    def __nonzero__(self):
        if self.x or self.y:
            return True
        else:
            return False
            
    def __eq__(self, point):
        return self.x==point.x and self.y==point.y
    def __lt__(self, other):
        "<"
        return abs(self)<abs(other)
    def __le__(self, other):
        "<="
        return abs(self)<=abs(other)
    def __gt__(self, other):
        ">"
        return abs(self)>abs(other)
    def __ge__(self, other):
        ">="
        return abs(self)>=abs(other)
        
    def __abs__(self):
        return hypot(self.x,self.y)
    def __add__(self, point):
        if isinstance(point, Point):
            return Point(self.x + point.x, self.y + point.y)
        else:
            raise TypeError
    def __sub__(self, point):
        if isinstance(point, Point):
            return Point(self.x - point.x, self.y - point.y)
        else:
            raise TypeError
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

def get_cross(point, vector):
    single_move = vector*(TILESIZE-1)/abs(vector)
    new_point = point + single_move
    i,j = (new_point/TILESIZE).get()
    return i,j



