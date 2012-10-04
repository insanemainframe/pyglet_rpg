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
            locations = []
            for j in range(J):
                loc_map = self.get_locmap(i,j)
                locations.append(loc_map)
            self.locations.append(locations)
    
    def get_locmap(self, I,J):
        loc_map = []
        for i in range(I*LOCATIONSIZE, (I+1)*LOCATIONSIZE):
            loc_row = []
            for j in range(J*LOCATIONSIZE, (J+1)*LOCATIONSIZE):
                loc_row.append(self.map[i][j])
            loc_map.append(loc_row)
        return loc_map
            
    def get_locations(self, position):
        return position/TILESIZE/LOCATIONSIZE
    
    def __getitem__(self,cord):
        i,j = cord
        I = i/LOCATIONSIZE
        J = j/LOCATIONSIZE
        return self.locations[I][J][i-I*LOCATIONSIZE][j-J*LOCATIONSIZE]

class Location:
    def __init__(self, i,j):
        self.new_events = False
        self.new_static_events = False
    
    def new_event(self):
        self.new_events = True
    
    def new_static_event(self):
        self.new_static_events = False
    
    def update(self):
        self.new_events = False
        self.new_static_events = False
        




    
if __name__=='__main__':
    world = World()
    
