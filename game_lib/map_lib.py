#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('../')

from math import hypot

from math_lib import Point
#import game

from config import TILESIZE

class MapTools:
    "методы работы с картой"
    def __init__(self, width, height):
        self.map_width = width
        self.map_height = height
        if height==width:
            self.map_size = height
    
    def resize_d(self, cord, dimension):
        "меняем координаты в случае превышения размера карты"
        if dimension=='width':
            size = self.map_width
        elif dimension=='height':
            size = self.map_height
        else:
            raise ValueError
        if cord < 0:
            return size + cord
        if cord > size:
            return size
        else:
            return cord    
    
    def resize(self, cord):
        "меняем координаты в случае превышения размера карты"
        if cord < 0:
            return self.map_size + cord
        if cord > self.map_size:
            return cord - self.map_size
        else:
            return cord      
    




class Steps(MapTools):
    def __init__(self,size):
        self.size = size
        self.map = {}
        self.lifetime = 100
    
    def look(self, position, rad):
        I,J = (position/TILESIZE).get()
        looked = set()
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    try:
                        step = self.map[i][j]
                    except KeyError, excp:
                        step = 0
                    looked.add(tuple((Point(i,j), step)))
        return looked
    
    def step(self, position):
        i,j = (position/TILESIZE).get()
        if not i in self.map:
            self.map[i] = {}
        self.map[i][j] = self.lifetime
    
    def update(self):
        for i in self.map:
            for j in self.map[i]:
                self.map[i][j]-=1


    
if __name__=='__main__':
    world = World()
    
