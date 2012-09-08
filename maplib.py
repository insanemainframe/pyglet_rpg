#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import TILESIZE, logger
from mathlib import Point
from math import hypot
from mapgen import load_map

class Map:
    "методы работы с картой"
    def resize(self, cord):
        "меняем координаты в случае превышения размера карты"
        if cord < 0:
            return self.size + cord
        if cord > self.size:
            return cord - self.size
        else:
            return cord        

class MetaMap:
    "разделяемое состояние объектов карты"
    @staticmethod
    def init():
        cls = MetaMap
        if not hasattr(cls,'created'):
            worldmap, size = load_map()
            cls.map = worldmap
            cls.size = size
            cls.objects = []
            cls.objects_updates = []
            cls.created = True
    @staticmethod
    def add_object(name):
        cls = MetaMap
        cls.objects.append(name)
    @staticmethod
    def move_on_map(name, vector):
        cls = MetaMap
        cls.objects_updates
        
            
        
    
class World(MetaMap, Map):
    "класс карты как со стороны ссервера"
    def __init__(self):
        self.init()
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




def test_client():
    world = ClientWorld()
    world.position = Point(10*TILESIZE,10*TILESIZE)
    for i in xrange(20):
        for j in xrange(20):
            world.insert([(Point(i,j),'n')])
    world.move_position(Point(20,20))
    print world.look_around(3*TILESIZE)
    
if __name__=='__main__':
    world = World()
    print len(world.look(Point(999,1001), 12))
    #test_client()
    
