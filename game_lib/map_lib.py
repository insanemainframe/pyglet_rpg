#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('../')

from math import hypot

from math_lib import Point
from mapgen import load_map

from config import TILESIZE

class MapTools:
    "методы работы с картой"
    def resize_d(self, cord, dimension):
        "меняем координаты в случае превышения размера карты"
        if dimension=='width':
            size = self.width
        elif dimension=='height':
            size = self.height
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
            return self.size + cord
        if cord > self.size:
            return cord - self.size
        else:
            return cord      
    
class World:
    "класс карты как со стороны ссервера"
    def __init__(self):
        World.map, World.size = load_map()
        print 'server world size',World.size

class MapObserver(MapTools):
    prev_looked = set()
    
    def look(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        position = self.position
        rad = self.look_size
        I,J = (position/TILESIZE).get()
        #
        new_updates = {}
        #
        observed = set()
        looked = set()
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    try:
                        tile_type = self.map[i][j]
                    except IndexError, excp:
                        pass
                    else:
                        looked.add(((i,j), tile_type))
                        observed.add((i,j))
                        if (i,j) in self.updates:
                            name,(position, vector, tilename) = self.updates[(i,j)]
                            new_updates[name] = (position, vector, tilename)
        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        return new_looked, observed, new_updates



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
    
