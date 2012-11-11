#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
xrange = range

from engine.mathlib import Cord, Position, ChunkCord
from engine.enginelib.meta import Updatable
from engine.enginelib.mutable import MutableObject



from weakref import ProxyType

class MapObserver:
    "mixn объекта видящего карту"
    def mixin(self, look_size):
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
        # print ('observe')

        self.prev_observed = self.fov

        self.fov = set()
        self.fov_voxels = []

        rad = self.look_size
        I,J = self.cord.get()

        i_start = self.location.resize_cord(I-rad)
        i_end = self.location.resize_cord(I+rad)
        j_start = self.location.resize_cord(J-rad)
        j_end = self.location.resize_cord(J+rad)

        for i in xrange(i_start, i_end):
            for j in xrange(j_start, j_end):
                if SQUARE_FOV or (I-i)**2 + (J-j)**2 < rad**2:
                    self.fov.add(Cord(i, j))
                    
                    voxel = self.location.get_voxel(Cord(i,j))
                    self.fov_voxels.append(voxel)


    
    def look_map(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        #cdef set map_tiles
        map_tiles = set()

        for cord in self.fov:
            if cord not in self.prev_observed:
                tile_type = self.location.get_tile(cord)
                map_tiles.add((cord, tile_type))

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


        #
        events = {}
        for player in self.observed_objects:
            if isinstance(player, MutableObject):
                events[player.gid] = player.get_events()
            

        return new_players, events, old_players_pairs



        
    

    
    
   