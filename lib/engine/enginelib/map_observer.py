#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug
xrange = range



from sets import ImmutableSet
from weakref import ProxyType


from engine.mathlib import Cord, Position, ChunkCord
from engine.enginelib.meta import Updatable
from engine.enginelib.mutable import MutableObject

class MapObserver:
    "mixn объекта видящего карту"
    def mixin(self, look_size):
        self.look_size = look_size
        self.look_radius = self.look_size*TILESIZE
        self.sq_look_size = look_size**2
        
        
        #ткущий фов
        self.fov = ImmutableSet()
        #новый фов
        self.new_fov = ImmutableSet()

        #список видимых контейнеров с объектами
        self.fov_voxels = dict()


        self.objects = []
        self.objects_gids = ImmutableSet()

        
    def clear_looked(self):
        self.fov = ImmutableSet()
        self.new_fov = ImmutableSet()
        self.old_fov = ImmutableSet()

        self.fov_voxels.clear()

        self.objects_gids = ImmutableSet()
        self.objects = []

    def handle_change_location(self):
        self.clear_looked()
        self.observe()


    def handle_respawn(self):
        self.clear_looked()
        self.observe()


    
    def observe(self):
        "формирует новую область видимости"
        #формируем видимые коордианты
        
        I,J = self.cord.get()

        rad = self.look_size
        sq_rad = self.sq_look_size

        i_start = self.location.resize_cord(I-rad)
        i_end = self.location.resize_cord(I+rad)
        j_start = self.location.resize_cord(J-rad)
        j_end = self.location.resize_cord(J+rad)




        #новые видимые коордианты
        fov_cords = ImmutableSet(
            (Cord(i,j) for i in xrange(i_start, i_end)
            for j in xrange(j_start, j_end)
            if RECT_FOV or (I-i)**2 + (J-j)**2 < sq_rad)
            )





        self.new_fov = fov_cords - self.fov
        self.old_fov = self.fov - fov_cords
        self.fov = fov_cords

        #обновляем словарь видимых вокселей
        new_voxels = {cord:self.location.get_voxel_full(cord) for cord in self.new_fov}

        for cord in self.old_fov:
            del self.fov_voxels[cord]

        self.fov_voxels.update(new_voxels)




    
    def look_map(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        #cdef ImmutableSet map_tiles

        new_tiles = [(cord, self.location.get_tile(cord)) for cord in self.new_fov]
                

        return new_tiles, self.fov


    def look_objects(self):
        objects = sum((voxel.values() for voxel in self.fov_voxels.values() if voxel), [])
        objects_gids = ImmutableSet([game_object.gid for game_object in objects])

        if objects_gids!=self.objects_gids:
            chunk = self.chunk

            new_players = [player.get_tuple(self.name) for player in objects
                            if player.gid not in self.objects_gids]

            old_players = self.objects_gids - objects_gids
                    

            self.objects = objects
            self.objects_gids = objects_gids

            old_players_pairs = [(name, chunk.delay_args.get(name)) for name in old_players]



            return new_players, old_players_pairs
        else:
            return None, None

    def look_events(self):        
        return [(gid, events) for gid, events in self.chunk.get_events() if gid in self.objects_gids]



        
    

    
    
   