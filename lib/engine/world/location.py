#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *
xrange = range


from share.point import Point

from engine.world.location_lib import ChoiserMixin, PersistentLocation
from engine.world.objects_containers import ActivityContainer

from engine.enginelib.meta import Container, Guided, HierarchySubject

from engine.world.chunk import Chunk, near_cords
from engine.world.voxel import Voxel


from weakref import proxy, ProxyType
from collections import defaultdict



class Location(PersistentLocation, ActivityContainer, ChoiserMixin):
    "базовый класс карты"
    monster_count = 0
    nears = []
    
    def __init__(self, game, name):
        PersistentLocation.__init__(self, name)
        ActivityContainer.__init__(self)

        self.game = game
        self.name = name
        
        
        self.teleports = [Point(self.size/2, self.size/2)]
        
        self.chunk_number = int(self.size/CHUNK_SIZE +1)
        
        
        self._players = {}
        
        self._chunks = []
        self.chunk_keys = []
        self.active_chunks = {}
        
        self.create_voxels()
        self.create_chunks()
        self.create_chunk_links()
        

    def new_object(self, player, chunk = None, position = None):
        assert chunk is None or isinstance(chunk, Point) and self.is_valid_chunk(chunk)
        assert position is None or isinstance(position, Point) and self.is_valid_position(position)
        
        if isinstance(player, Guided):  print ('\n location.new_object %s' % player)
        self.game._new_object(player)
        
        self.add_object(proxy(player), chunk, position)


    def add_object(self, player, chunk = None, position = None):
        assert isinstance(player, ProxyType)
        assert chunk is None or isinstance(chunk, Point)
        assert not hasattr(player, 'location')

        if isinstance(player, Guided):  print ('location.add_object %s ' % player)

        if not position:
            if not chunk:
                chunk = self.main_chunk.cord
            (chunk_i, chunk_j), position = self.choice_position(player, chunk)
        else:
            chunk_i, chunk_j = self.get_chunk_cord(position).get()

        new_chunk = self.get_chunk_by_cord(chunk_i, chunk_j)

        player.location = proxy(self)
        new_chunk.add_object(player)

        player.set_position(position)

        cord = position/TILESIZE
        self.add_to_voxel(player, cord)
        

        self._players[player.name] = player
        self.add_activity(player)

        player.location_changed = True
        player.handle_new_world()




    def pop_object(self, player):
        if isinstance(player, Guided):  print ('location.pop_object %s' % player)
        assert player.name in self._players
       
        name = player.name
        prev_chunk = player.chunk

        prev_chunk.pop_object(player)
        self.pop_from_voxel(player)

        self.remove_activity(player)
        del self._players[name]
        del player.location
        player.location_changed = True

    

    def remove_object(self, player):
        "вызывает remove_object синглетона"
        if isinstance(player, Guided):  print ('\n location.remove_object', player)

        if isinstance(player, HierarchySubject):
            player.unbind_all_slaves()

        if isinstance(player, Container):
            player.unbind_all()

        self.game._remove_object(player)


    
    def change_chunk(self, player, new_chunk_cord):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        assert isinstance(player, ProxyType)

        if isinstance(player, Guided):  print ('location.change_chunk %s' % player)

        ci, cj = new_chunk_cord.get()

        if 0<=ci<self.chunk_number and 0<cj<self.chunk_number :
            cur_chunk = self._chunks[ci][cj]
                            
            player.chunk.pop_object(player)
            cur_chunk.add_object(player)


    def change_cord(self, player, new_cord):
        assert isinstance(player, ProxyType)
        assert isinstance(new_cord, Point)
        assert player.cord!=new_cord

        if 0<=new_cord.x<self.size and 0<new_cord.y<self.size:
            self.pop_from_voxel(player)
            self.add_to_voxel(player, new_cord)

            player.cord = new_cord
            player.cord_changed = True
        else:
            print ("location: change_cord, key error", new_cord)

    def get_chunk_cord(self, position):
        "возвращает координаты локации для заданой позиции"
        return position/TILESIZE/CHUNK_SIZE
    
    
    def get_chunk_by_cord(self, chunk_i,chunk_j):
        return self._chunks[chunk_i][chunk_j] 

    def get_chunk(self, position):
        "возвращает слокацию"
        
        chunk_i,chunk_j = self.get_chunk_cord(position).get()
        try:
            return self._chunks[chunk_i][chunk_j]
        except IndexError as Error:
            print('Warning: invalid chunk cord %s[%s:%s]' % (self.name,chunk_i,chunk_j))
            raise Error

    def is_valid_chunk(self, chunk_cord):
            x,y = chunk_cord.get()
            return 0<x<self.chunk_number and 0<y<self.chunk_number

    def is_valid_cord(self, i, j):
        return 0<i<self.size and 0<j<self.size

    def is_valid_position(self, position):
        x,y = position.get()
        return 0<x<self.position_size and 0<y<self.position_size
    
    def get_near_voxels(self, i,j):
        "возвращает список соседних тайлов"

        cords = [(i+ni, j+nj) for ni,nj in near_cords if self.is_valid_cord(i+ni, j+nj)]
        tiles = [self.map[i][j] for i,j in cords]
        return tiles

    def get_near_cords(self, i,j):
        "возвращает список соседних тайлов"
        cords = [(i+ni, j+nj) for ni,nj in near_cords if self.is_valid_cord(i+ni, j+nj)]
        return cords

    def get_voxel(self, i, j):
        return self._voxels[i,j]
    
    def add_to_voxel(self, player, cur_cord):
        assert isinstance(player, ProxyType)

        voxel = self._voxels[cur_cord.get()]
        voxel.append(player)
        player.cord_changed = True
        
    def pop_from_voxel(self, player):
        voxel = player.voxel
        voxel.remove(player)
        player.cord_changed = True
    
    

        
    def set_activity(self):
        print ('set_activity')
        self.game.add_active_location(self)
    
    def unset_activity(self):
        print ('unset_activity')
        self.game.remove_active_location(self)

    

    def create_voxels(self):
        self._voxels = {}
        for i in range(self.size):
            for j in range(self.size):
                self._voxels[i,j] = Voxel(Point(i,j))

    def create_chunks(self):
        "создает локации"
        n = self.chunk_number
        
        for i in xrange(n):
            row = []
            for j in xrange(n):
                row.append(Chunk(self, i,j))
                self.chunk_keys.append((i,j))
            self._chunks.append(row)

        mi = mj = int(self.chunk_number/2)
        self.main_chunk = self._chunks[mi][mj]

    def create_chunk_links(self):
        "создает ссылки в локациях"
        for row in self._chunks:
            for chunk in row:
                chunk.create_links(self._chunks)

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

    
    
    
        
    def handle_over_range(self, player, position):
        pass
    
    
    
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


    def start(self):
        result = self.load_objects()
        if not result:
            self.generate_func(self)

        number = len(self._players)
        print ('Location "%s" with %s objects has been started' % (self.name, number))


                
    
    

