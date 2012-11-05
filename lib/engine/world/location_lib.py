#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *
xrange = range

from share.point import Point
from share.serialization import loads, dumps, load, dump


from engine.world.chunk import Chunk, near_cords
from engine.world.map_source import load_map
from engine.enginelib import meta 
from engine import game_objects

from random import randrange, choice
from weakref import proxy,ProxyType
from os.path import exists


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
        for i in xrange(n):
            monster = object_type()
            self.new_object(monster)
            
    
    def create_item(self, n, object_type):
        n = int(n/LOCATION_MUL)
        for i in xrange(n):
                item = object_type()
                self.new_object(item)
        



    def load_objects(self):
        if self.location_exists():
            filename = LOCATION_PATH % self.mapname + LOCATION_FILE
            locations_objects = load(filename)


            for object_type, data, (x,y) in locations_objects:
                object_type = self.get_class(object_type)
                data = object_type.__load__(*data)
                player = object_type(*data)
                self.new_object(player, position = Point(x,y))
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
            if isinstance(player, meta.Savable):
                object_type = player.__class__.__name__
                data = player.__save__()
                position = player.position.get()

                objects.append((object_type, data, position))


        return objects






class ChoiserMixin:
    def choice_position(self, player, chunk = None, radius = 0):
        "выбирает случайную позицию, доступную для объекта"
        print( '%s: choice_position %s' % (self.name, player))
        start_chunk = chunk
        assert start_chunk is None or isinstance(start_chunk, Point)

        MAX_RADIUS = (self.chunk_number/2)
        if radius>=MAX_RADIUS:
            radius = MAX_RADIUS-1

        ignore_chunk = False
        ignore_position = False

        chunks_with_bad = set()
        bad_chunks = set()

        err_message = 'No place for %s: %s %s' % (player, start_chunk, radius)


        while radius<=MAX_RADIUS:
            if not start_chunk:
                chunk_keys = set(self.chunk_keys[:])
            else:
                i,j = start_chunk
                chunk_keys = set(self.chunk_in_radius(i,j, radius = radius))

            if not ignore_position:
                chunk_keys-=chunks_with_bad
            if not ignore_chunk:
                chunk_keys-=bad_chunks

            chunk_keys = list(chunk_keys)

            while chunk_keys:
                chunk_i, chunk_j = chunk_keys.pop(randrange(0, len(chunk_keys)))
                
                chunk = self._chunks[chunk_i][chunk_j]



                if hasattr(player, 'verify_chunk'):
                    is_good_chunk = player.verify_chunk(self, chunk)
                    if not is_good_chunk:
                        bad_chunks.add((chunk_i, chunk_j))
                else:
                    is_good_chunk = True

                if ignore_chunk or is_good_chunk:
                    try:
                        position = self._choice_in_chunk(player, chunk, ignore_position)
                    except NoPlaceException:
                        chunks_with_bad.add((chunk_i, chunk_j))
                    else:
                        assert isinstance(position, Point)

                        return (chunk_i, chunk_j), position

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


    def _choice_in_chunk(self, player, chunk, ignore_position = False):
        tile_cords = chunk.tile_keys[:]
        while tile_cords:
            tile_i, tile_j = choice(tile_cords)
            tile_cords.remove((tile_i, tile_j))



            if not ignore_position:

                if hasattr(player, 'verify_position'):
                    is_good_tile = player.verify_position(self, chunk, tile_i, tile_j)
                else:
                    is_good_tile = True
                if is_good_tile:
                    shift = Point(randrange(TILESIZE), randrange(TILESIZE))
                    position = Point(tile_i, tile_j)*TILESIZE + shift
                    return position
            else:
                shift = Point(randrange(TILESIZE), randrange(TILESIZE))
                position = Point(tile_i, tile_j)*TILESIZE + shift
                return position
        raise NoPlaceException()
            
    
    def chunk_in_radius(self, I, J, radius):
        if not radius:
            return [(I,J)]
        else:
            start_i = self.resize_chunk_cord(I - radius)
            end_i = self.resize_chunk_cord(I + radius)
            start_j = self.resize_chunk_cord(J - radius)
            end_j = self.resize_chunk_cord(I + radius )

            chunk_cords = []
            for i in range(start_i, end_i):
                for j in range(start_j, end_j):
                    if 0<i<self.chunk_number and 0<j<self.chunk_number:
                        chunk_cords.append((i,j))
            return chunk_cords

    def resize_chunk_cord(self, cord):
        if cord<0:
            return 0
        elif cord>self.chunk_number:
            return self.chunk_number
        else:
            return cord


