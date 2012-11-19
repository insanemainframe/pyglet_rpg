#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug
from share.errors import *

from engine.mathlib cimport Cord, Position, ChunkCord
from cpython cimport bool



from random import randrange, choice
from weakref import proxy,ProxyType
from collections import defaultdict



class ChoiserMixin:
    def mixin(self):
        self.generation = True

    def flush_genaration_data(self):
        self.generation = False


    def choice_position(self, player, ChunkCord chunk = ChunkCord(0,0), int radius = 0, bool generation = False):
        "выбирает случайную позицию, доступную для объекта"
        cdef set bad_chunks, bad_cords
        cdef bool ignore_chunk, ignore_position
        cdef ChunkCord start_chunk
        cdef Position position
        cdef int MAX_RADIUS
        

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



            chunk_list = list(chunks)
            del chunks

            while chunk_list:
                chunk_cord = chunk_list.pop(randrange(len(chunk_list)))
                choisen_chunk = self._chunks[chunk_cord]

                if ignore_chunk or player.verify_chunk(self, choisen_chunk):

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
                        debug('ignore_chunk')
                        ignore_chunk = True
                    else:
                        if not ignore_position:
                            debug('ignore_position')
                            ignore_position = True
                        else:
                            raise NoPlaceException(err_message)
            else:
                if not ignore_chunk:
                    debug('ignore_chunk')
                    ignore_chunk = True
                else:
                    if not ignore_position:
                        debug('\n\n ignore_position')
                        ignore_position = True
                    else:
                        raise NoPlaceException(err_message)

        raise NoPlaceException(err_message)

    def _choice_in_chunk(self, player, ChunkCord chunk_cord, set bad_cords, bool ignore_position):
        cdef list cords
        cdef Cord cord
        cdef Position position, shift
        cdef list voxel

        chunk = self._chunks[chunk_cord]

        cords = list(self.get_free_cords(chunk_cord))

        while cords:
            cord = cords.pop(randrange(len(cords)))
            voxel = self.get_voxel(cord)

            if not self.get_tile(cord) in player.BLOCKTILES:
                if ignore_position or player.verify_position(self, chunk, cord):
                    position = cord.to_position()
                    if not player.cord_binded:
                        shift = Position(randrange(TILESIZE), randrange(TILESIZE))
                        position += shift 
                    return position
            bad_cords.add(cord)
        raise NoPlaceException




            
    
    

    



