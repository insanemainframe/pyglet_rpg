#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('../')

from share.mathlib import Point, NullPoint
from mapgen import load_map

from config import *



class World:
    "класс карты как со стороны ссервера"
    def __init__(self):
        World.map, World.size = load_map()
        print 'server world size',World.size
        self.locations = []
        self.create_locations()
    
    def create_locations(self):
        I = self.size/LOCATIONSIZE
        J = self.size/LOCATIONSIZE
        for i in range(I):
            self.locations.append([])
            for j in range(J):
                loc_map = self.map[I*LOCATIONSIZE: (I+1)*LOCATIONSIZE]
                loc_map = loc_map[J*LOCATIONSIZE: (J+1)*LOCATIONSIZE]
                self.locations[i].append(Location(i,j, loc_map))
    
    def get_locations(self, position):
        return position/TILESIZE/LOCATIONSIZE

class Location:
    def __init__(self, i,j, loc_map):
        self.i, self.j = i,j
        self.players = {}
        self.map = loc_map
        self.solid_objects = {}
        self.events = {}
    
    def clear(self):
        self.events = {}




    
if __name__=='__main__':
    world = World()
    
