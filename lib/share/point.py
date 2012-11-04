#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from math import hypot, floor


    
class Point:
    "класс точек и векторов"
    def __init__(self,x=0,y=0):        
        self.x = int(x)
        self.y = int(y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __nonzero__(self):
        return bool(self.x) or bool(self.y)

    def __eq__(self, point):
        assert isinstance(point, Point)
        return self.x==point.x and self.y==point.y

    def __ne__(self, point):
        assert isinstance(point, Point)
        return self.x!=point.x or self.y!=point.y

    def __lt__(self, point):
        "<"
        assert isinstance(point, Point)
        return abs(self)<abs(point)

    def __le__(self, point):
        "<="
        assert isinstance(point, Point)
        return abs(self)<=abs(point)

    def __gt__(self, point):
        ">"
        assert isinstance(point, Point)
        return abs(self)>abs(point)

    def __ge__(self, point):
        ">="
        assert isinstance(point, Point)
        return abs(self)>=abs(point)

    def __abs__(self):
        return hypot(self.x,self.y)

    def __add__(self, point):
        assert isinstance(point, Point)
        return Point(self.x + point.x, self.y + point.y)

    def __sub__(self, point):
        "-"
        assert isinstance(point, Point)
        return Point(self.x - point.x, self.y - point.y)

    def __neg__(self):
        return Point(-self.x, -self.y)
        
    def __mul__(self, number):
        '*'
        return Point(self.x*number, self.y*number)

    def __div__( self,  number):
        return Point(floor(self.x/number), floor(self.y/number))
    
    def __truediv__( self,  number):
        return Point(floor(self.x/number), floor(self.y/number))

    def get(self):
        return (self.x, self.y)

    def in_radius(self, point, radius):
        assert isinstance(point, Point)

        return ((self.x-point.x)**2 +(self.y-point.y)**2) <= radius**2

    def __repr__(self):
        return "%s:%s" % self.get()
    def __hash__(self):
        return hash((self.x, self.y))
        

