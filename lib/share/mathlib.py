#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from math import hypot, floor
from config import *


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
    def __init__(self,x=0,y=0):
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
    def __ne__(self, point):
        return self.x!=point.x or self.y!=point.y
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

    def __div__( self,  number):
        return Point(floor(self.x/number), floor(self.y/number))
    
    def __truediv__( self,  number):
        return Point(floor(self.x/number), floor(self.y/number))

    def get(self):
        return (self.x, self.y)
    def __repr__(self):
        return "%s:%s" % self.get()
    def __hash__(self):
        return hash((self.x, self.y))
        
