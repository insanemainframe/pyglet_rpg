#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.game import game
from share.map import *
from share.mathlib import *
from engine.game_lib import Event

from math import hypot

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
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    tile_type = game.world.map[i][j]
                    observed.add((i,j))
                    looked.add((Point(i,j), tile_type))
                        

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        
        return new_looked, observed
        
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
        
    def look_static(self):
        "поиск видимых сатических объеков и их событий"
        radius = self.look_size*TILESIZE
        
        static_events = set()
        for (i,j), eventlist in game.static_events.items():
            dist = abs(Point(i,j)*TILESIZE - self.position)
            if dist<=radius:
                static_events.update([event for event in eventlist])
        
        static_objects = {}
        for (i,j), objectlist in game.static_objects.items():
            dist = abs(Point(i,j)*TILESIZE - self.position)
            if dist<=radius:
                for name, static_object in objectlist.items():
                    static_objects[name] = static_object.get_tuple()
        
        return static_objects, static_events
