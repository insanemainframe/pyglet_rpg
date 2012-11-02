#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import Point

from engine.world.world_persistence import PersistentWorld
from engine.world.chunk import Chunk, near_cords
from engine.events import Event
from engine.enginelib.meta import DynamicObject, StaticObject
from engine.world.objects_containers import ActivityContainer


from random import randrange, choice
from weakref import proxy
from collections import defaultdict
from time import time
import imp



class MetaWorld(PersistentWorld, ActivityContainer):
    "базовый класс карты"
    monster_count = 0
    nears = []
    
    def __init__(self, game, name):
        PersistentWorld.__init__(self, name)
        ActivityContainer.__init__(self)

        self.game = game
        self.name = name
        
        
        self.teleports = [Point(self.size/2, self.size/2)]
        
        self.chunk_number = self.size/CHUNK_SIZE +1
        
        self.tiles = defaultdict(list)
        
        self.players = {}
        
        self.chunks = []
        self.chunk_keys = []
        self.active_chunks = {}
        
        self.create_chunks()
        self.create_links()


        init = imp.load_source('init', WORLD_PATH %name + 'init.py')
        self.generate_func = init.generate
    
    def start(self):
        result = self.load_objects()
        if not result:
            self.generate_func(self)

        
    def set_activity(self):
        print 'set_activity'
        self.game.add_active_world(self)
    
    def unset_activity(self):
        print 'unset_activity'
        self.game.remove_active_world(self)

    
    def create_chunks(self):
        "создает локации"
        n = self.chunk_number
        
        for i in xrange(n):
            row = []
            for j in xrange(n):
                row.append(Chunk(self, i,j))
                self.chunk_keys.append((i,j))
            self.chunks.append(row)
        mi = mj = int(self.chunk_number/2)
        self.main_chunk = self.chunks[mi][mj]

    def add_active_chunk(self, chunk):
        self.active_chunks[chunk.cord.get()] = proxy(chunk)

    def remove_active_chunk(self, chunk):
        key = chunk.cord.get()
        if key in self.active_chunks:
            del self.active_chunks[key]

    def get_active_chunks(self):
        return self.active_chunks.values()

    def has_active_chunks(self):
        return bool(self.active_chunks)

    
    def create_links(self):
        "создает ссылки в локациях"
        for row in self.chunks:
            for chunk in row:
                chunk.create_links()

    def add_object(self, player):
        self.players[player.name] = proxy(player)
        self.add_activity(player)

    def pop_object(self, player):
        name = player.name
        player.chunk.pop_object(player)
        if name in self.players:
            del self.players[name]
        self.remove_activity(player)

    
    def new_object(self, player):
        player.world = self
        player.handle_creating()
        
        chunk = self.get_chunk(player.position)
        chunk.add_object(player)
        player.chunk = chunk
        
        cord = player.position/TILESIZE
        self.add_to_tile(player, cord)
        
        self.game.new_object(player)
        self.add_object(player)

    def remove_object(self, player):
        player.chunk.pop_object(player)
        self.pop_from_tile(player, player.cord)
        self.pop_object(player)
        self.game.remove_object(player)


    
    def change_chunk(self, player, prev_loc, cur_loc):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        pi, pj = prev_loc.get()
        prev_chunk = self.chunks[pi][pj]
        ci, cj = cur_loc.get()
        if 0<ci<self.chunk_number and 0<cj<self.chunk_number :
            
            cur_chunk = self.chunks[ci][cj]
                            
            prev_chunk.pop_object(player)
            cur_chunk.add_object(player)
            
            
            player.chunk = cur_chunk
            
            for related in player.related_objects:
                related.chunk = cur_chunk
        else:
            return prev_chunk
    
    def get_loc_cord(self, position):
        "возвращает координаты локации для заданой позиции"
        return position/TILESIZE/CHUNK_SIZE
    
    
    def get_chunk(self, position):
        "возвращает слокацию"
        
        i,j = (position/TILESIZE/CHUNK_SIZE).get()
        try:
            return self.chunks[i][j]
        except IndexError as Error:
            print('Warning: invalid chunk cord %s[%s:%s]' % (self.name,i,j))
            raise Error
    
    def get_near_tiles(self, i,j):
        "возвращает список соседних тайлов"
        insize = lambda i,j: 0<i<self.size and 0<j<self.size
        cords = [(i+ni, j+nj) for ni,nj in near_cords if insize(i+ni, j+nj)]
        tiles = [self.map[i][j] for i,j in cords]
        return tiles

    def get_near_cords(self, i,j):
        "возвращает список соседних тайлов"
        insize = lambda i,j: 0<i<self.size and 0<j<self.size
        cords = [(i+ni, j+nj) for ni,nj in near_cords if insize(i+ni, j+nj)]
        return cords
    
    def add_to_tile(self, player, cur_cord):
        self.tiles[cur_cord.get()].append(player)
        
    def pop_from_tile(self, player, cur_cord):
        tile = self.tiles[cur_cord.get()]
        if player in tile:
            tile.remove(player)
    
    def update_tiles(self, player, prev_cord, cur_cord):
        tile = self.tiles[prev_cord.get()]
        if player in tile:
            tile.remove(player)

        self.tiles[cur_cord.get()].append(player)
    
        
    
    def choice_position(self, player, start_chunk = False, radius = 0):
        "выбирает случайную позицию, доступную для объекта"
        print 'choice_position'
        MAX_RADIUS = (self.chunk_number/2)

        ignore_chunk = False
        ignore_position = False

        if not start_chunk:
            chunk_keys = self.chunk_keys[:]
            
        else:
            chunk_keys = self.chunk_in_radius(*start_chunk.cord.get(), radius = radius)
            
            if radius>=MAX_RADIUS:
                radius = MAX_RADIUS-1

        

        while radius<MAX_RADIUS:
            while chunk_keys:
                chunk_i, chunk_j = choice(chunk_keys)
                chunk_keys.remove((chunk_i, chunk_j))
                chunk = self.chunks[chunk_i][chunk_j]

                if hasattr(player, 'choice_chunk'):
                    is_good_chunk = player.choice_chunk(self, chunk)
                else:
                    is_good_chunk = True

                if ignore_chunk or is_good_chunk:
                    tile_cords = chunk.tile_keys[:]
                    while tile_cords:
                        tile_i, tile_j = choice(tile_cords)
                        tile_cords.remove((tile_i, tile_j))

                        is_free = not bool(self.tiles[(tile_i, tile_j)])
                        non_block = not self.map[tile_i][tile_j] in player.BLOCKTILES


                        if ignore_position or (is_free and non_block):

                            if hasattr(player, 'choice_position'):
                                is_good_tile = player.choice_position(self, chunk, tile_i, tile_j)
                            else:
                                is_good_tile = True
                            if is_good_tile:
                                shift = Point(randrange(TILESIZE), randrange(TILESIZE))
                                position = Point(tile_i, tile_j)*TILESIZE + shift
                                return position
            if start_chunk and not ignore_chunk:
                if radius>=MAX_RADIUS:
                    ignore_chunk = True
                else:
                    radius +=1
                    chunk_keys = self.chunk_in_radius(*start_chunk.cord.get(), radius = radius)
                    ignore_chunk = False
                print 'radius+1'
            elif not ignore_chunk:
                print 'Generation %s: ignore_chunk' % player
                ignore_chunk = True
            elif not ignore_position:
                print 'Generation %s: ignore_position' % player
                ignore_position = True
            else:
                break

        raise NoPlaceException('No place for %s: %s %s' % (player, start_chunk, radius))
            
    
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
                    chunk_cords.append((i,j))
            print 'chunk_in_radius', radius, len(chunk_cords)
            return chunk_cords


    def handle_over_range(self, player, position):
        pass
    
    
    
    def create_object(self, n, object_type):
        n = int(n/WORLD_MUL)
        for i in xrange(n):
            position = self.choice_position(object_type)
            name = object_type.__name__
            
            monster = object_type('%s_%s' % (name, self.game.monster_count) , position)
            
            self.new_object(monster)
            
            self.game.monster_count+=1
    
    def create_item(self, n, object_type):
        n = int(n/WORLD_MUL)
        for i in xrange(n):
            try:
                position = self.choice_position(object_type)
            except :
                print 'geebration error'
            else:
                item = object_type(position)
                
                self.new_object(item)
    
    def resize(self,cord):
        if cord<0:
            return 0
        elif cord>self.size:
            return self.size
        else:
            return cord

    def resize_chunk_cord(self, cord):
        if cord<0:
            return 0
        elif cord>self.chunk_number:
            return self.chunk_number
        else:
            return cord
                
    
    

class NoPlaceException(BaseException):
    pass