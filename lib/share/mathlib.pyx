#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from math import hypot, floor
from config import *


from cpython cimport bool

cdef class Point:
    "класс точек и векторов"
    def __init__(self, int x, int y):
        self.x = x
        self.y = y


    def __richcmp__(Point self, Point point, int op):
        if op==0:
            return abs(self)<abs(point)
        elif op==1:
            return abs(self)<=abs(point)
        elif op==2:
            return self.x==point.x and self.y==point.y
        elif op==3:
            return self.x!=point.x or self.y!=point.y
        elif op==4:
            return abs(self)>abs(point)
        elif op==5:
            return abs(self)>=abs(point)

    def __iter__(self):
        yield self.x
        yield self.y
            
    def __nonzero__(Point self):
        return bool(self.x) or bool(self.y)

    def __bool__(self):
        return bool(self.x) or bool(self.y)

    def __abs__(Point self):
        return hypot(self.x,self.y)
    
    def __add__(Point self, Point point):
        return Point(self.x + point.x, self.y + point.y)
    
    def __sub__(Point self, Point point):
        "-"
        return Point(self.x - point.x, self.y - point.y)
    def __neg__(Point self):
        return Point(-self.x, -self.y)
    
    def __mul__(Point self, float number):
        '*'
        return Point(self.x*number, self.y*number)
    
    def __div__(Point self, float number):
        return Point(floor(self.x/number), floor(self.y/number))
    
    def __truediv__(Point self, float number):
        return Point(floor(self.x/number), floor(self.y/number))

    cpdef tuple get(Point self):
        return (self.x, self.y)

    cpdef bool in_radius(self, Point point, float radius):
        return ((self.x-point.x)**2 +(self.y-point.y)**2) <= radius**2

    def __repr__(Point self):
        return "%s:%s" % self.get()

    def __hash__(Point self):
        return hash((self.x, self.y))
        
