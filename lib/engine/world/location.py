#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from engine.errors import *

from share.point import Point

from engine.world.location_lib import ChoiserMixin, PersistentLocation
from engine.world.objects_containers import ActivityContainer

from engine.enginelib.meta import Container

from engine.world.chunk import Chunk, near_cords
from engine.world.voxel import Voxel


from weakref import proxy, ProxyType
from collections import defaultdict



class Metalocation(PersistentLocation, ActivityContainer, ChoiserMixin):
    "базовый класс карты"
    monster_count = 0
    nears = []
    
    def __init__(self, game, name):
        PersistentLocation.__init__(self, name)
        ActivityContainer.__init__(self)

        self.game = game
        self.name = name
        
        
        self.teleports = [Point(self.size/2, self.size/2)]
        
        self.chunk_number = self.size/CHUNK_SIZE +1
        
        self.tiles = defaultdict(lambda: Voxel())
        
        self._players = {}
        
        self.chunks = []
        self.chunk_keys = []
        self.active_chunks = {}
        
        self.create_chunks()
        self.create_links()
        
    
    def start(self):
        result = self.load_objects()
        if not result:
            self.generate_func(self)

        
    def set_activity(self):
        print 'set_activity'
        self.game.add_active_location(self)
    
    def unset_activity(self):
        print 'unset_activity'
        self.game.remove_active_location(self)

    
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
        assert isinstance(player, ProxyType)

        self._players[player.name] = player
        self.add_activity(player)

    def pop_object(self, player, delay_args = False):
        name = player.name
        if name in self._players:
            player.chunk.pop_object(player, delay_args)
            self.pop_from_tile(player, player.cord)
            self.remove_activity(player)
            del self._players[name]


    
    def new_object(self, player):
        self.game.new_object(player)

        player_ref = proxy(player)

        player.location = self
        player.handle_creating()
        
        chunk = self.get_chunk(player.position)
        chunk.add_object(player_ref)
        player.chunk = chunk
        
        cord = player.position/TILESIZE
        self.add_to_tile(player_ref, cord)
        
        
        self.add_object(player_ref)

    def remove_object(self, player):
        player.chunk.pop_object(player)
        
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
            cur_chunk.add_object(proxy(player))
            
            
            player.chunk = cur_chunk
            
            if isinstance(player, Container):
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
        assert isinstance(player, ProxyType)

        self.tiles[cur_cord.get()].append(player)
        
    def pop_from_tile(self, player, cur_cord):
        tile = self.tiles[cur_cord.get()]
        tile.remove(player)
    
    def update_tiles(self, player, prev_cord, cur_cord):
        player = proxy(player)

        tile = self.tiles[prev_cord.get()]
        if player in tile:
            tile.remove(player)

        self.tiles[cur_cord.get()].append(player)
    
        
    def handle_over_range(self, player, position):
        pass
    
    
    
    def create_object(self, n, object_type):
        n = int(n/LOCATION_MUL)
        for i in xrange(n):
            position = self.choice_position(object_type)
            name = object_type.__name__
            
            monster = object_type('%s_%s' % (name, self.game.monster_count) , position)
            
            self.new_object(monster)
            
            self.game.monster_count+=1
    
    def create_item(self, n, object_type):
        n = int(n/LOCATION_MUL)
        for i in xrange(n):
            try:
                position = self.choice_position(object_type)
            except NoPlaceException:
                print 'generation error'
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


    def debug(self):
        for row in self.chunks:
            for chunk in row:
                chunk.debug()

        for player in self._players:
            try:
                player.__doc__
            except ReferenceError as error:
                print('%s %s' % (error, self.name))
   
                
    
    

