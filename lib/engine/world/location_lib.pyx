#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *
xrange = range

from engine.mathlib cimport Cord, Position, ChunkCord
from cpython cimport bool

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
            try:
                self.new_object(monster)
            except NoPlaceException:
                print 'NoPlaceException', object_type.__name__
            
    
        
        



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

    def flush_genaration_data(self):
        self.bad_tiles.clear()


    def choice_position(self, player,  ChunkCord start_chunk = ChunkCord(0,0), int radius = 0):
        "выбирает случайную позицию, доступную для объекта"
        cdef set bad_chunks, bad_cords
        cdef bool ignore_chunk, ignore_position
        cdef int MAX_RADIUS
        cdef list chunks_list

        print( '%s: choice_position %s' % (self.name, player))

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
                print 'start_chunk', player, start_chunk
                chunks = set(self.chunks_in_radius(*start_chunk.get(), radius = radius))
                
            else:
                
                chunks = set(self.get_chunk_cords())

            if not ignore_chunk:
                chunks -= bad_chunks



            chunks_list = list(chunks)

            print 'chunks_list: ', len(chunks_list)

            while len(chunks_list)>0:
                print 'try chunk'
                chunk_cord = chunks_list.pop(randrange(len(chunks_list)))
                chunk = self[chunk_cord]

                if ignore_chunk or ignore_position or player.verify_chunk(self, chunk):
                    chunk = self[chunk_cord]

                    try:
                        position = self._choice_in_chunk(player, chunk_cord, bad_cords, ignore_position)
                    except NoPlaceException:
                        print 'no position for %s' % player
                        bad_chunks.add(chunk_cord)
                    else:
                        return chunk_cord, position
                else:
                    print 'not player.verify_chunk ', player
                    if start_chunk:
                        bad_chunks.add(chunk_cord)
                    
            print 'end chunks loop'
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
                            raise NoPlaceException('1: No place for' % player)
            else:
                if not ignore_chunk:
                    print('ignore_chunk')
                    ignore_chunk = True
                else:
                    if not ignore_position:
                        print('ignore_position')
                        ignore_position = True
                    else:
                        raise NoPlaceException('2: No place for' % player)

        raise NoPlaceException('3: No place for' % player)

    def _choice_in_chunk(self, player,  chunk_cord, set bad_cords, bool ignore_position):
        cdef list cords, BLOCKTILES
        cdef Position position, shift
        cdef Cord cord
        cdef int i,j

        chunk = self[chunk_cord]

        cords = chunk.get_free_cords()
        BLOCKTILES = player.BLOCKTILES

        if not cords:
            print 'no free cords'
            raise NoPlaceException('no free cords')

        print 'cord', len(cords)

        while len(cords)>0:
            cord = cords.pop(randrange(len(cords)))
            voxel = chunk[cord]
            i,j = cord.get()
            if not self.get_tile(cord) in BLOCKTILES:
                if ignore_position or player.verify_position(self, chunk, voxel, i,j):
                    shift = Position(randrange(TILESIZE), randrange(TILESIZE))
                    position = cord.to_position() + shift 
                    return position
            # bad_cords.add(cord)
        else:
            print 'end of cord loop'

        raise NoPlaceException('no good cords')




            
    
    def chunks_in_radius(self, int I, int J, int radius):
        cdef int start_i, start_j, end_i, end_j, i, j,chunk_number
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
                    yield ChunkCord(i,j)

    def resize_chunk_cord(self, cord):
        if cord<0:
            return 0
        elif cord>self.chunk_number:
            return self.chunk_number
        else:
            return cord



