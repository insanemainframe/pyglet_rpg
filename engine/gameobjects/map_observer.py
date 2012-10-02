#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.game import game
from share.map import *
from share.mathlib import *

from math import hypot

class MapObserver(MapTools):
    "класс объекта видящего карту"
    prev_looked = set()
    prev_observed = set()
    def __init__(self, look_size):
        MapTools.__init__(self, game.size, game.size)
        self.look_size = look_size
    def look(self):
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
                    try:
                        tile_type = game.world.map[i][j]
                    except IndexError, excp:
                        pass
                    else:
                        observed.add((i,j))
                        looked.add((Point(i,j),tile_type))
                        

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        
        new_events, static_objects, static_events = self.look_objects()
        
        return new_looked, observed, new_events, static_objects, static_events
    
    def look_objects(self):
        rad = self.look_size*TILESIZE
        location = self.get_location()
        
        new_events = set()
        for event in location.events:
            position = event.position
            if abs(position-self.position)<=rad:
                new_events.add(event)
        
        static_objects = {}
        for (i,j), static_object_list in location.static_objects.items():
            position = Point(i,j)*TILESIZE
            if abs(position-self.position)<=rad:
                for name, static_object in static_object_list.items():
                    #print 'static_objects', location.static_objects
                    stype = static_object.__class__.__name__
                    static_objects[name] = (stype, static_object.position)
        
        static_events = set()
        for event in location.static_events:
            position = event.position
            if abs(position-self.position)<=rad:
                static_events.add(event)
                
            
        return new_events, static_objects, static_events
    
    
    def _look_tile(self, i,j, tile_type, looked, observed, new_events, static_objects, static_events):
        looked.add((Point(i,j), tile_type))
        observed.add((i,j))
        #ищем события в этом тайле
        if (i,j) in game.events:
            for event in game.events[(i,j)]:
                if event.name==self.name:
                    event.object_type = 'Self'
                new_events.add(event)
                
        #ищем события статических объектов
        if (i,j) in game.static_events:
            for event in game.static_events[(i,j)]:
                static_events.add(event)
                
        #ищем статические объекты
        if (i,j) in game.static_objects:
            tile_static_objects = {name: (static_object.__class__.__name__, static_object.position)
                for name, static_object in game.static_objects[(i,j)].items()}
            
            static_objects.update(tile_static_objects)
        
        return looked, observed, new_events, static_objects

