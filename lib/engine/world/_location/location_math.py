#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *


from engine.mathlib import Cord, Position, ChunkCord
from engine.world.chunk import Chunk


from engine.world.objects_containers import near_cords

from collections import defaultdict



class LocationMath:
    def create_chunks(self):
        "создает локации"
        n = self.chunk_number
        cords = [ChunkCord(i,j) for i in xrange(n) for j in xrange(n)]
        self._chunks = {cord: Chunk(self, cord) for cord in cords if self.is_valid_chunk(cord)}

        main_chunk_cord = ChunkCord(n/2, n/2)
        self.main_chunk = self._chunks[main_chunk_cord]

    def create_chunk_links(self):
        "создает ссылки в локациях"
        for chunk in self._chunks.values():
            chunk.create_links()

    def create_voxels(self):
        _range = range(self.size)
        self._voxels = {Cord(i,j): {} for i in _range for j in _range}


    def generate_free_cords(self):
        self._free_cords = {}
        
        for chunk_cord in self._chunks:
            self._free_cords[chunk_cord] = set()
            for cord in chunk_cord:
                if self.is_valid_cord(cord):
                    self._free_cords[chunk_cord].add(cord)

         
        for chunk_cord, cord_list in self._free_cords.items():
            x,y = chunk_cord.get()
            if 0<x<self.chunk_number-1 and 0<y<self.chunk_number-1:
                assert cord_list, (chunk_cord, self.chunk_number)

            for cord in cord_list:
                assert isinstance(cord, Cord)





    def is_valid_chunk(self, chunk_cord):
        assert isinstance(chunk_cord ,ChunkCord)
        x,y = chunk_cord.get()
        return 0<=x<self.chunk_number and 0<=y<self.chunk_number


    def is_valid_cord(self, cord):
        assert isinstance(cord, Cord)
        x,y = cord.get()
        return 0<=x<self.size and 0<=y<self.size

    def is_valid_position(self, position):
        assert isinstance(position, Position)
        x,y = position.get()
        return 0<=x<self.position_size and 0<=y<self.position_size
          



    def get_tile(self, cord):
        assert isinstance(cord, Cord)
        assert self.is_valid_cord(cord)
        return self.map[cord.x][cord.y]

    def get_near_tiles(self, cord):
        nears = [(cord+near_cord).get()  for near_cord in near_cords if self.is_valid_cord(cord+near_cord)]

        return [self.map[i][j] for i,j in nears]

    def get_voxel(self, cord):
        assert isinstance(cord, Cord)
        return self._voxels[cord].values()

    def get_near_voxels(self, cord):
        nears = [cord+near_cord for near_cord in near_cords]
        return [self._voxels[cord].values() for cord in nears if self.is_valid_cord(cord)]
    

    
    

    def get_free_cords(self,  chunk_cord, block_tiles = []):
    
        return self._free_cords[chunk_cord]


    
    def chunks_in_radius(self, I, J, radius):
        if not radius:
            yield ChunkCord(I,J)
        else:
            start_i = self.resize_chunk_cord(I - radius)
            end_i = self.resize_chunk_cord(I + radius)
            start_j = self.resize_chunk_cord(J - radius)
            end_j = self.resize_chunk_cord(I + radius )

            for i in range(start_i, end_i):
                for j in range(start_j, end_j):
                    if 0<i<self.chunk_number and 0<j<self.chunk_number:
                        yield ChunkCord(i,j)
    

    
    
    def resize_cord(self,cord):
        if cord<0:
            return 0
        elif cord>self.size:
            return self.size
        else:
            return cord

    def resize_position(self, cord):
        if cord<0:
            return 0
        elif cord>self.position_size:
            return self.position_size
        else:
            return cord

    def resize_chunk_cord(self, cord):
        if cord<0:
            return 0
        elif cord>self.chunk_number:
            return self.chunk_number
        else:
            return cord

