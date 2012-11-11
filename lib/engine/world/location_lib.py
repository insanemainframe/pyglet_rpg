#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *
xrange = range

from engine.mathlib import Cord, Position, ChunkCord

from share.serialization import loads, dumps, load, dump

from engine.world.chunk import Chunk
from engine.world.map_source import load_map
from engine.enginelib.meta  import Savable, SavableRandom
from engine import game_objects

from random import randrange, choice
from weakref import proxy,ProxyType
from os.path import exists
from collections import defaultdict


import imp





class PersistentLocation(object):
    def __init__(self, mapname):
        self.mapname = mapname
        print ('loading map...')
        self.map, self.size, self.background = load_map(mapname)
        self.position_size = self.size*TILESIZE

        init = imp.load_source('init', LOCATION_PATH %mapname + 'init.py')
        self.generate_func = init.generate

        



    def create_object(self, n, object_type):
        n = int(n/LOCATION_MUL)
        print 'creating %s of %s' % (n, object_type.__name__)
        for i in xrange(n):
            monster = object_type()
            self.new_object(monster, generation = True)
            
    
        
        



    def load_objects(self):
        if self.location_exists():
            filename = LOCATION_PATH % self.mapname + LOCATION_FILE
            locations_objects = load(filename)


            for object_type, data, (x,y) in locations_objects:
                position = Position(x,y)
                object_type = self.get_class(object_type)

                player = object_type.__load__(proxy(self), *data)

                # if isinstance(player, SavableRandom):
                #     chunk, position = self.choice_position(player)
                #     self.new_object(player, chunk = chunk, position = position)
                # else:
                self.new_object(player, position = position)
            return True
        else:
            return False




    def get_class(self, object_type):
        return getattr(game_objects, object_type)

    def location_exists(self):
        return exists(LOCATION_PATH % self.mapname + LOCATION_FILE)
            
    
    def save(self, force = False):
        if SAVE_LOCATION or force:
            locations_objects = self.save_objects()
            filename = LOCATION_PATH % self.mapname + LOCATION_FILE
            data = dump(locations_objects, filename)



    def save_objects(self):
        objects = []

        for player in self._players.values():
            if isinstance(player, Savable):
                object_type = player.__class__.__name__
                data = player.__save__()
                position = player.position.get()

                objects.append((object_type, data, position))


        return objects






class ChoiserMixin:
    def mixin(self):
        self.bad_tiles = defaultdict(set)
        self.bad_chunks = defaultdict(set)
        self.generation = True

    def flush_genaration_data(self):
        self.generation = False
        self.bad_tiles.clear()


    def choice_position(self, player, chunk = None, radius = 0, generation = False):
        "выбирает случайную позицию, доступную для объекта"

        print( '%s: choice_position %s' % (self.name, player))
        start_chunk = chunk
        assert start_chunk is None or isinstance(start_chunk, ChunkCord)

        MAX_RADIUS = (self.chunk_number/2)
        if radius>=MAX_RADIUS:
            radius = MAX_RADIUS-1

       
        bad_chunks = set()
        bad_cords = set()
        ignore_chunk = False
        ignore_position = False

        #if isinstance(player, type):


        while radius<=MAX_RADIUS:
            if start_chunk:
                chunks = set(self.chunks_in_radius(*start_chunk.get(), radius = radius))
                
            else:
                chunks = set(self.get_chunk_cords())

            if not ignore_chunk:
                chunks -= bad_chunks



            chunks = list(chunks)
            while chunks:
                chunk_cord = chunks.pop()
                chunk = self[chunk_cord]

                if ignore_chunk or player.verify_chunk(self, chunk):
                    chunk = self[chunk_cord]

                    try:
                        position = self._choice_in_chunk(player, chunk_cord, bad_cords, ignore_position)
                    except NoPlaceException:
                        bad_chunks.add(chunk_cord)
                    else:
                        return chunk_cord, position
                else:
                    bad_chunks.add(chunk_cord)
                    
        
            if start_chunk:
                if radius<MAX_RADIUS:
                    radius+=1
                else:
                    if not ignore_chunk:
                        print('ignore_chunk')
                        ignore_chunk = True
                    else:
                        if not ignore_position:
                            print('ignore_position')
                            ignore_position = True
                        else:
                            raise NoPlaceException(err_message)
            else:
                if not ignore_chunk:
                    print('ignore_chunk')
                    ignore_chunk = True
                else:
                    if not ignore_position:
                        print('ignore_position')
                        ignore_position = True
                    else:
                        raise NoPlaceException(err_message)

        raise NoPlaceException(err_message)

    def _choice_in_chunk(self, player, chunk_cord, bad_cords, ignore_position):
        chunk = self[chunk_cord]

        cords = list(chunk.get_free_cords())

        while cords:
            cord = cords.pop()
            voxel = chunk[cord]
            i,j = cord.get()
            if ignore_position or player.verify_position(self, chunk, voxel, i,j):
                shift = Position(randrange(TILESIZE), randrange(TILESIZE))
                position = cord.to_position() + shift 
                return position
            else:
                bad_cords.add(cord)
        raise NoPlaceException




            
    
    def chunks_in_radius(self, I, J, radius):
        # cdef int start_i, start_j, end_i, end_j
        # cdef list chunk_cords


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

    def resize_chunk_cord(self, cord):
        if cord<0:
            return 0
        elif cord>self.chunk_number:
            return self.chunk_number
        else:
            return cord



