#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import TILESIZE, logger
from mathlib import Point
from math import hypot
from mapgen import load_map

class MetaWorld:
    @staticmethod
    def set_map(worldmap, size):
        MetaWorld.map = worldmap
        MetaWorld.size = size
    @staticmethod
    def resize(cord):
        "меняем координаты в случае превышения размера карты"
        if cord < 0:
            return MetaWorld.size + cord
        if cord > MetaWorld.size:
            return cord - MetaWorld.size
        else:
            return cord
    @staticmethod
    def resize_point(point):
        point = point
        return Point(MetaWorld.resize(point.x), MetaWorld.resize(point.y))
    
class World(MetaWorld):
    "класс карты как со стороны ссервера"
    def __init__(self):
        self.set_map(*load_map())
        print 'server world size', self.size

            
    def look(self, position, rad):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        I,J = (position/TILESIZE).get()
        looked = set()
        look_count = 0
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    try:
                        tile_type = self.map[i][j]
                        look_count+=1
                    except IndexError, excp:
                        pass
                    else:
                        looked.add(tuple((Point(i,j), tile_type)))
        return looked


class ClientWorld(MetaWorld):
    "клиентская карта"
    def __init__(self, world_size):
        size = world_size
        print 'clientworld size', size
        self.map = [[None for j in xrange(size)] for i in xrange(size)]
        
    def move_position(self, vector):
        "перемещаем камеру"
        self.position = self.position + vector
        
    def insert(self, tiles):
        "обновляет карту, добавляя новые тайлы, координаты - расстояние от стартовой точки"
        for point, tile_type in tiles:
            self.map[point.x][point.y] = tile_type
            
    def look_around(self, rad):
        "список тайлов в поле зрения (координаты в тайлах от позиции камеры, тип)"
        rad = int(rad/TILESIZE)+2
        I,J = (self.position/TILESIZE).get()
        looked = set()
        look_count = 0
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                i,j = self.resize(i), self.resize(j)
                tile_type = self.map[i][j]
                if tile_type:
                    look_count+=1
                else:
                    tile_type = 'fog'
                point = (Point(i,j)*TILESIZE)-self.position
                looked.add((point, tile_type))
        i, j = self.position.get()
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
    
