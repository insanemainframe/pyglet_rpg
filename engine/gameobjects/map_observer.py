#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *

from math import hypot



class MapObserver:
    "класс объекта видящего карту"
    def __init__(self, look_size):
        self.look_size = look_size
        self.look_radius = self.look_size*TILESIZE
        
        self.prev_players = []
        self.prev_static_objects = []
        
        self.prev_looked = set()
        self.prev_observed = set()
    
    def resize(self,cord):
        if 0<=cord<=self.world.size:
            return cord
        else:
            if cord>self.world.size:
                return self.world.size
            else:
                return 0
    
    def look_map(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        position = self.position
        rad = self.look_size
        I,J = (position/TILESIZE).get()
        #
        observed = set()
        looked = set()
        #
        i_start = self.resize(I-rad)
        i_end = self.resize(I+rad)
        j_start = self.resize(J-rad)
        j_end = self.resize(J+rad)
        
        for i in xrange(i_start, i_end):
            for j in xrange(j_start, j_end):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    if (i,j) not in self.prev_observed:
                        tile_type = self.world.map[i][j]
                        looked.add((Point(i,j), tile_type))
                    observed.add((i,j))

        self.prev_observed = observed
        return looked, observed
        
    def in_radius_(self, position):
        dist = abs(position - self.position)
        return dist<=self.look_radius
    
    def in_radius(self, position):
        cord = (position/TILESIZE).get()
        return cord in self.prev_observed
    
    def is_self_player(self, name, object_type, position, args):
        if name==self.name:
            object_type = 'Self'
        return name, object_type, position, args
    
    def look_players(self, force = False):
        all_players = self.location.get_players_list()
        players = {}
        
        for player in all_players:
            if self.in_radius(player.position):
                gid = player.gid
                players[gid] = self.is_self_player(*player.get_tuple())
        
        players_names = players.keys()
        if players_names!=self.prev_players:
            result = players
        else:
            result = {}
        self.prev_players = players_names
        if not force:
            return result
        else:
            return players
        
    
    def look_static_objects(self, force = False):
        all_static_objects = self.location.get_static_objects_list()
        
        static_objects = {}
        
        for static_object in all_static_objects:
            if self.in_radius(static_object.position):
                gid = static_object.gid
                static_objects[gid] = static_object.get_tuple()
        
        names = static_objects.keys()
        if names!=self.prev_static_objects:
            result = static_objects
        else:
            result = {}
        self.prev_static_objects = names
        
        if not force:
            return result
        else:
            return static_objects

    
    def look_events(self):
        "поиск вдимывх событий"
        events = set()
        for event in self.location.get_events():
            if self.in_radius(event.position):
                events.add(event)
                
        return events
        
    def look_static_events(self):
        "поиск видимых сатических объеков и их событий"        
        static_events = set()
        for static_event in self.location.get_static_events():
            if self.in_radius(static_event.position):
                static_events.add(static_event)
                
        return static_events
    
    
