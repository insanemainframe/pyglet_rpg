#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *

from math import hypot

lhypot = hypot

class MapObserver:
    "класс объекта видящего карту"
    def __init__(self, look_size):
        self.look_size = look_size
        self.look_radius = self.look_size*TILESIZE
        
        self.prev_players = []
        self.prev_static_objects = []
        
        self.prev_looked = set()
        self.prev_observed = set()
    

    
    def look_map(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        rad = self.look_size
        I,J = self.cord.get()
        #
        observed = set()
        looked = set()
        #
        i_start = self.world.resize(I-rad)
        i_end = self.world.resize(I+rad)
        j_start = self.world.resize(J-rad)
        j_end = self.world.resize(J+rad)
        
        for i in xrange(i_start, i_end):
            for j in xrange(j_start, j_end):
                if lhypot(I-i,J-j) < rad:
                    if (i,j) not in self.prev_observed:
                        tile_type = self.world.map[i][j]
                        looked.add((Point(i,j), tile_type))
                    observed.add((i,j))

        self.prev_observed = observed
        return looked, observed
        
    
    def in_radius(self, cord):
        "проверяет находится позиция в обозримых тайлах"
        i,j = cord.get()
        I,J = self.cord.get()
        diff = lhypot(I-i,J-j)
        return diff<self.look_size
    
    def is_self_player(self, name, object_type, position, args):
        "проверяет, являетя видимый игрок наблюдателем и меняет класс на Self"
        if name==self.name:
            object_type = 'Self'
        return name, object_type, position, args
    
    def look_players(self, force = False):
        "список видимых игроков, если не изменился - пустой список"
        all_players = self.location.get_players_list()
        players = {}
        
        for player in all_players:
            if self.in_radius(player.cord):
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
        "выдает список видимых статических объектов, или пустой список если он не измеинлся"
        all_static_objects = self.location.get_static_objects_list()
        
        static_objects = {}
        
        for static_object in all_static_objects:
            if self.in_radius(static_object.cord):
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
            if self.in_radius(event.cord):
                events.add(event)
        
        return events
        
    def look_static_events(self):
        "поиск видимых статических событий"        
        static_events = set()
        for static_event in self.location.get_static_events():
            if self.in_radius(static_event.cord):
                static_events.add(static_event)
                
        return static_events
    
    
