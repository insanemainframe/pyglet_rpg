#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.game import game
from share.map import *
from share.mathlib import *
from engine.game_lib import Event

from math import hypot

def resize(cord):
    if 0<=cord<=game.world.size:
        return cord
    else:
        if cord>game.world.size:
            return game.world.size
        else:
            return 0

class MapObserver(MapTools):
    "класс объекта видящего карту"
    def __init__(self, look_size):
        MapTools.__init__(self, game.size, game.size)
        self.look_size = look_size
        self.look_radius = self.look_size*TILESIZE
        
        self.prev_players = []
        self.prev_static_objects = set()
        self.prev_looked = set()
        self.prev_observed = set()
        
    def look_map(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        position = self.position
        rad = self.look_size
        I,J = (position/TILESIZE).get()
        #
        observed = set()
        looked = set()
        #
        i_start = resize(I-rad)
        i_end = resize(I+rad)
        j_start = resize(J-rad)
        j_end = resize(J+rad)
        
        for i in xrange(i_start, i_end):
            for j in xrange(j_start, j_end):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    if (i,j) not in self.prev_observed:
                        tile_type = game.world.map[i][j]
                        looked.add((Point(i,j), tile_type))
                    observed.add((i,j))

        self.prev_observed = observed
        return looked, observed
        
    def is_self(self, event):
        if event.name!=self.name:
            return event
        else:
            return Event(event.name, 'Self', event.position, event.action, event.args)
    
    def is_self_player(self, name, object_type, position, args):
        if name==self.name:
            object_type = 'Self'
        return object_type, position, args
    
    def look_players(self):
        all_players = self.location.get_players_list()
        players = {}
        
        for player in all_players:
            dist = abs(player.position - self.position)
            if dist<=self.look_radius:
                name = player.name
                players[name] = self.is_self_player(name, *player.get_tuple())
        
        players_names = players.keys()
        if players_names!=self.prev_players:
            result = players
        else:
            result = None
        self.prev_players = players_names
        return result
        
    
    def look_events(self):
        "поиск вдимывх событий"
        events = set()
        for event in self.location.get_events():
            dist = abs(event.position - self.position)
            if dist<=self.look_radius:
                events.add(event)
                
        return events
        
    def look_static_events(self):
        "поиск видимых сатических объеков и их событий"        
        static_events = set()
        for static_event in self.location.get_static_events():
            dist = abs(static_event.position - self.position)
            if dist<=self.look_radius:
                static_events.add(static_event)
                
        return static_events
    
    def look_static_objects(self):
        look_radius = self.look_size*TILESIZE
        all_static_objects = self.location.get_static_objects_list()
        
        static_objects = {}
        
        for static_object in all_static_objects:
            dist = abs(static_object.position - self.position)
            if dist<=self.look_radius:
                name = static_object.name
                static_objects[name] = static_object.get_tuple()
        
        return static_objects
