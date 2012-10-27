#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import DynamicObject, StaticObject
from share.mathlib import Point





class MapObserver:
    "класс объекта видящего карту"
    def __init__(self, look_size):
        self.look_size = look_size
        self.look_radius = self.look_size*TILESIZE
        
        self.prev_players  = {}

        
        self.prev_looked = set()
        self.prev_observed = set()

        self.fov = set()

    def handle_change_world(self):
        self.clear_looked()

    def handle_respawn(self):
        self.clear_looked()

    def clear_looked(self):
        self.prev_players  = {}
        self.prev_looked = set()
        self.prev_observed = set()

        self.fov = set()
    
    def observe(self):
        self.prev_observed = self.fov.copy()

        self.fov.clear()

        rad = self.look_size
        I,J = self.cord.get()

        i_start = self.world.resize(I-rad)
        i_end = self.world.resize(I+rad)
        j_start = self.world.resize(J-rad)
        j_end = self.world.resize(J+rad)

        for i in xrange(i_start, i_end):
            for j in xrange(j_start, j_end):
                if SQUARE_FOV or (I-i)**2 + (J-j)**2 < rad**2:
                    self.fov.add((i, j))

    
    def look_map(self, for_events = True, for_objects = True):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        #
        map_tiles = set()

        players  = {}
        events = {}

        #

        
        for i,j in self.fov:
                if (i,j) not in self.prev_observed:
                    tile_type = self.world.map[i][j]
                    map_tiles.add((Point(i,j), tile_type))

                tile = self.world.tiles[Point(i,j)]

                for game_object in tile:
                    gid = game_object.gid

                    if for_objects:
                        players[gid] = game_object.get_tuple(name = self.name)

                    if for_events:
                        events[gid] = game_object.get_events()


        self.prev_players = players

        return (map_tiles, self.fov), (players, events), 
        
    

    
    def is_self_player(self, name, object_type, position, args):
        "проверяет, являетя видимый игрок наблюдателем и меняет класс на Self"
        if name==self.name:
            object_type = 'Self'
        return name, object_type, position, args
    
   