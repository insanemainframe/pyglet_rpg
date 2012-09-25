#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('../')

from math import hypot

from math_lib import Point
#import game

from config import TILESIZE






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
    
