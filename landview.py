#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Объект представляет собой копию видимой карты
from config import *
from mathlib import Point

class LandView(GameWindow):
    def __init__(self, shift, rad):
        self.position = shift
        self.map = {}
        
    def set_shift(self):
        self.position+=vector
        
    def insert(self, tiles):
        """добавляет новые тайлы в представление карты"""
        for x,y, tilename in tiles:
            self.map[(x,y)] = tilename
    

    def map_range(self):
        "видимые на экране тайлы"
        rad = self.window_size
        start = (i-rad)/TILESIZE*TILESIZE
        end = ((i+rad)/TILESIZE+1)*TILESIZE
        
        return ((self.size-j if j>self.size else j) for j in range(start, end, TILESIZE))
        
    def lookup(self):
        i,j = self.position.get()
        for x in self.map_range(i):
            for y in self.map_range(j):
                if self.map.has_key((i,j)):
                    yield (i,j, self.map[i,j])
    def update(self):
        self.tiles = [self.create_tile(Point(i,j), tilename) for i,j,tilename in self.lookup()]
        
        
