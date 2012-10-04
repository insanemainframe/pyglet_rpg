#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import Point, NullPoint
from mapgen import load_map

from weakref import proxy


class World:
    "класс карты как со стороны ссервера"
    def __init__(self):
        self.map, self.size = load_map()
        self.location_size = self.size/LOCATIONSIZE
        print 'creting world size',self.size
        self.locations = []
        self.create_locations()
        self.create_links()
    
    def create_locations(self):
        for i in range(self.location_size):
            locations = []
            for j in range(self.location_size):
                locations.append(Location(self, i,j))
            self.locations.append(locations)
    
    def create_links(self):
        for row in self.locations:
            for location in row:
                location.create_links()
    
    def get_loc_cord(self, position):
        return (position/TILESIZE/LOCATIONSIZE).get()
    

near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]

class Location:
    "небольшие локаци на карте, содержат ссылки на соседние локации и хранят ссылки на объекты и события"
    def __init__(self, world, i,j):
        self.world = proxy(world)
        self.i, self.j = i,j
        self.cord = Point(i,j)
        
        self.new_events = False
        self.new_static_events = False
        
        self.players = {}
        self.static_objects = {}
        self.solid = {}
        
        self.nears = []
        
    def create_links(self):
        #создаем сслки на соседние локации
        for i,j in near_cords:
            try:
                near_location = self.world.locations[self.i+i][self.j+j]
            except IndexError:
                pass
            else:
                self.nears.append(proxy(near_location))
    
    def add_player(self, player):
        from engine_lib import DynamicObject, StaticObject
        if isinstance(player, DynamicObject):
            self.players[player.name] = proxy(player)
            if isinstance(player, engine_lib.Solid):
                self.solid[player.name] = proxy(player)
        else:
            raise TypeError('add_player: %s not DynamicObject instance' % player.name)
    
    def remove_player(self, player):
        if isinstance(player, engine_lib.Solid):
                del self.solid[player.name]
        del self.players[player.name]

            
    def get_players(self):
        players = self.players.copy()
        [players.update(location.players) for location in self.nears]
        
        return players



    def add_static_object(self, player):
        from engine_lib import DynamicObject, StaticObject
        if isinstance(player, StaticObject):
            self.static_objects[player.name] = proxy(player)
            if isinstance(player, engine_lib.Solid):
                self.solid[player.name] = proxy(player)
        else:
            raise TypeError('add_static_object: %s not StaticObject instance' % player.name)
    
    def remove_static_object(self, player):
        if isinstance(player, engine_lib.Solid):
            del self.solid[player.name]
        del self.static_objects[player.name]

    
    def get_static_objects(self):
        static_objects = self.static_objects.copy()
        [static_objects.update(location.static_objects) for location in self.nears]
        return static_objects
    
    def get_solid(self):
        solid = self.solid.copy()
        [solid.update(location.solid) for location in self.nears]
        return solid
    
    def new_event(self):
        self.new_events = True
    
    def new_static_event(self):
        self.new_static_events = True
    
    def check_events(self):
        for location in self.nears:
            if location.new_events:
                return True
        return False
    
    def check_static_events(self):
        for location in self.nears:
            if location.new_static_events:
                return True
        return False
    
    def update(self):
        self.new_events = False
        self.new_static_events = False
        
def init():
    from game import game
    global game
    import engine_lib
    global engine_lib

