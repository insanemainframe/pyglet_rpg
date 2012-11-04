#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import Point
from engine.enginelib.meta import Updatable

from weakref import ProxyType

class MapObserver:
    "класс объекта видящего карту"
    def __init__(self, look_size):
        self.look_size = look_size
        self.look_radius = self.look_size*TILESIZE
        
        
        self.prev_looked = set()
        self.prev_observed = set()


        self.observed_objects = []
        self.observed_objects_gids = set()
        self.observed_names = []

        self.fov = set()
        self.fov_voxels = [] #список видимых контейнеров с объектами

    def handle_change_location(self):
        self.clear_looked()

    def handle_respawn(self):
        self.clear_looked()

    def clear_looked(self):
        self.prev_looked = set()
        self.prev_observed = set()

        self.observed_objects_gids.clear()
        self.observed_objects = []
        self.observed_names = []

        self.fov.clear()
        self.fov_voxels = []
    
    def observe(self):
        #cdef int rad, I,J, i,j, i_start, i_end, j_start, j_end
        #cdef list tile
        print 'observe'

        self.prev_observed = self.fov.copy()

        self.fov.clear()
        self.fov_voxels = []

        rad = self.look_size
        I,J = self.cord.get()

        i_start = self.location.resize(I-rad)
        i_end = self.location.resize(I+rad)
        j_start = self.location.resize(J-rad)
        j_end = self.location.resize(J+rad)

        for i in xrange(i_start, i_end):
            for j in xrange(j_start, j_end):
                if SQUARE_FOV or (I-i)**2 + (J-j)**2 < rad**2:
                    self.fov.add((i, j))
                    
                    voxel = self.location.get_voxel(i,j)
                    self.fov_voxels.append(voxel)


    
    def look_map(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        #cdef set map_tiles
        map_tiles = set()

        for i,j in self.fov:
                if (i,j) not in self.prev_observed:
                    tile_type = self.location.map[i][j]
                    map_tiles.add((Point(i,j), tile_type))

        return map_tiles, self.fov


    def look_objects(self):
        #cdef set observed_objects_gids, old_players
        #cdef list observed_objects, new_players

        observed_objects = sum(self.fov_voxels, [])
        observed_objects_gids = set([game_object.gid for game_object in observed_objects])

        new_players = [player.get_tuple(self.name) for player in observed_objects
                        if player.gid not in self.observed_objects_gids]

        old_players = self.observed_objects_gids - observed_objects_gids
                

        self.observed_objects = observed_objects
        self.observed_objects_gids = observed_objects_gids
        self.observed_names = [player.name for player in observed_objects]

        old_players_pairs = []
        for name in old_players:
            if name in self.chunk.delay_args:
                delay_arg = self.chunk.delay_args[name]
            else:
                delay_arg = None

            old_players_pairs.append((name, delay_arg))


        ###debug
        for player in self.observed_objects:
            assert isinstance(player, ProxyType)

        return new_players, old_players_pairs

    def look_events(self):
        #cdef dict events
        events = {}
        for player, name in zip(self.observed_objects,self.observed_names):
            try:
                if isinstance(player, Updatable):
                    events[player.gid] = player.get_events()
                    #print player.name, events[player.gid]
            except ReferenceError:
                print "ReferenceError: %s" % name
                raw_input()
        

        return events

        
    

    
    
   