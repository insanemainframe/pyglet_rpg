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
                locations.append(Location(i,j))
            self.locations.append(locations)
    
            
    def get_loc_cord(self, position):
        return (position/TILESIZE/LOCATIONSIZE).get()
    
    def __getitem__(self,cord):
        i,j = cord
        I = i/LOCATIONSIZE
        J = j/LOCATIONSIZE
        return self.locations[I][J][i-I*LOCATIONSIZE][j-J*LOCATIONSIZE]

near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                Point(-1,0),Point(1,0),
            Point(-1,-1),Point(0,-1),Point(1,-1))]

class Location:
    def __init__(self, i,j):
        self.i, self.j = i,j
        self.cord = Point(i,j)
        self.new_events = False
        self.new_static_events = False
    
    def new_event(self):
        self.new_events = True
    
    def new_static_event(self):
        self.new_static_events = False
    
    def check_events(self):
        for I,J in near_cords:
            location = game.world.locations[self.i+I][self.j+J]
            if location.new_events:
                return True
        return False
    
    def check_static_events(self):
        for I,J in near_cords:
            location = game.world.locations[self.i+I][self.j+J]
            if location.new_static_events:
                return True
        return False
    
    def update(self):
        self.new_events = False
        self.new_static_events = False
        


def init():
    from game import game
    global game
