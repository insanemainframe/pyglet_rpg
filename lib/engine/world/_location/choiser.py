#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug
from share.errors import *

from engine.mathlib import Cord, Position, ChunkCord



from random import randrange, choice
from weakref import proxy,ProxyType
from collections import defaultdict



class ChoiserMixin:
    def mixin(self):
        self.generation = True

    def flush_genaration_data(self):
        self.generation = False


    def choice_position(self, player, chunk = None, radius = 0, generation = False):
        "выбирает случайную позицию, доступную для объекта"

        #debug( '%s: choice_position %s' % (self.name, player))

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
                chunk = self._chunks[chunk_cord]

                if ignore_chunk or player.verify_chunk(self, chunk):
                    chunk = self._chunks[chunk_cord]

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

    def _choice_in_chunk(self, player, chunk_cord, bad_cords, ignore_position):
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




            
    
    

    



