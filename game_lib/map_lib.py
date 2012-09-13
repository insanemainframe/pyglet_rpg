#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('../')

from math import hypot

from math_lib import Point
from mapgen import load_map

from config import TILESIZE, logger

class Map:
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
    
class World(Map):
    "класс карты как со стороны ссервера"
    def __init__(self):
        self.map, self.size = load_map()
        print 'server world size', self.size

            
    def look(self, position, rad):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        I,J = (position/TILESIZE).get()
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
                        looked.add(tuple((Point(i,j), tile_type)))
        return looked





    
if __name__=='__main__':
    world = World()
    
