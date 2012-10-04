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
    prev_looked = set()
    prev_observed = set()
    def __init__(self, look_size):
        MapTools.__init__(self, game.size, game.size)
        self.look_size = look_size
        
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
            
    def look_events(self):
        "поиск вдимывх событий"
        radius = self.look_size*TILESIZE
        events = set()
        for cord in self.prev_observed:
            if cord in game.events:
                eventlist = game.events[cord]
                events.update([self.is_self(event) for event in eventlist])
                    
        return events
        
    def look_static_events(self):
        "поиск видимых сатических объеков и их событий"
        radius = self.look_size*TILESIZE
        
        static_events = set()
        for (i,j), eventlist in game.static_events.items():
            dist = abs(Point(i,j)*TILESIZE - self.position)
            if dist<=radius:
                static_events.update([event for event in eventlist])
        return static_events
    
    def look_static_objects(self):
        radius = self.look_size*TILESIZE
        static_objects = {}
        for name, static_object in game.static_objects.items():
            dist = abs(static_object.position - self.position)
            if dist<=radius:
                    static_objects[name] = static_object.get_tuple()
        
        return static_objects
