#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *
xrange = range


from engine.mathlib import Cord, Position, ChunkCord


from engine.world.persistence import PersistentLocation
from engine.world.choiser import ChoiserMixin

from engine.world.objects_containers import ActivityContainer, near_cords

from engine.enginelib.meta import Container, Guided, HierarchySubject

from engine.world.chunk import Chunk


from weakref import proxy, ProxyType
from collections import defaultdict



class Location(PersistentLocation, ActivityContainer, ChoiserMixin):
    "базовый класс карты"
    monster_count = 0
    nears = []
    
    def __init__(self, game, name):
        PersistentLocation.__init__(self, name)
        ActivityContainer.__init__(self)
        ChoiserMixin.mixin(self)

        self.game = game
        self.name = name
        
        
        self.teleports = [Cord(self.size/2, self.size/2)]
        
        self.chunk_number = int(self.size/CHUNK_SIZE +1)
        
        
        self._players = {}
        
        self._chunks = {}
        self.active_chunks = {}
        
        self.create_chunks()
        self.create_chunk_links()
        self.create_voxels()


        

    def new_object(self, player, chunk = None, position = None):
        assert not (chunk and position), 'chunk and position conflict %s %s' % (chunk, position)
        assert chunk is None or self.is_valid_chunk(chunk), chunk
        assert position is None or self.is_valid_position(position), position

        
        
        if isinstance(player, Guided):  print ('\n location.new_object %s' % player)
        self.game._new_object(player)
        
        self.add_object(proxy(player), chunk, position)


    def add_object(self, player, chunk = None, position = None):
        assert isinstance(player, ProxyType)
        assert chunk is None or isinstance(chunk, ChunkCord)
        assert not hasattr(player, 'location')

        if isinstance(player, Guided):  print ('location.add_object %s ' % player)

        try:
            if not position:
                if chunk:
                    chunk_cord, position = self.choice_position(player, chunk)
                else:
                    chunk_cord, position = self.choice_position(player)
            else:
                if not self.is_valid_position(position):
                    position = Position(self.resize_position(position.x), self.resize_position(position.y))
                chunk_cord = position.to_chunk()

        except NoPlaceException as error:
            print 'add_object %s' % error
            raise error

        else:
            player.location = proxy(self)

            new_chunk = self._chunks[chunk_cord]
            new_chunk.add_object(player, position)

            cord = position.to_cord()
            self.add_to_voxel(player, cord)



            self._players[player.name] = player
            self.add_activity(player)

            player.location_changed = True
            player.handle_new_location()




    def pop_object(self, player):
        if isinstance(player, Guided):  print ('location.pop_object %s' % player)
        assert player.name in self._players
       
        name = player.name

        prev_chunk = player.chunk
        prev_chunk.pop_object(player)

        prev_cord = player.cord
        self.pop_from_voxel(player, prev_cord)

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

    def add_to_voxel(self, player, cord):
        assert isinstance(cord, Cord)
        assert not hasattr(player, 'voxel')

        voxel = self._voxels[cord]
        voxel[player.name] = player

        player.voxel = voxel
        player.cord = cord

        player.cord_changed = True

    def pop_from_voxel(self, player, cord):
        assert isinstance(cord, Cord)

        voxel = self._voxels[cord]

        del voxel[player.name]
        del player.voxel
        del player.cord

        player.cord_changed = True



    def change_voxel(self, player, new_cord):
        prev_cord = player.cord

        self.pop_from_voxel(player, prev_cord)
        self.add_to_voxel(player, new_cord)
    
    def change_chunk(self, player, new_chunk_cord, position):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        assert isinstance(player, ProxyType)

        if isinstance(player, Guided):  print ('location.change_chunk %s' % player)


        if self.is_valid_chunk(new_chunk_cord):
            prev_chunk = player.chunk
            cur_chunk = self._chunks[new_chunk_cord]
                            
            prev_chunk.pop_object(player)
            cur_chunk.add_object(player, position)



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
          


    

    def add_active_chunk(self, chunk):
        self.active_chunks[chunk.cord.get()] = proxy(chunk)

    def remove_active_chunk(self, chunk):
        key = chunk.cord.get()
        if key in self.active_chunks:
            del self.active_chunks[key]

    def get_active_chunks(self):
        return self.active_chunks.values()

    def get_chunk(self, chunk_cord):
        assert isinstance(chunk_cord, ChunkCord)
        assert self.is_valid_chunk(chunk_cord), chunk_cord

        return self._chunks[chunk_cord]

    def get_chunk_cords(self):
        return self._chunks.keys()

    def has_active_chunks(self):
        return bool(self.active_chunks)



    def get_tile(self, cord):
        assert isinstance(cord, Cord)
        assert self.is_valid_cord(cord)
        return self.map[cord.x][cord.y]

    def get_near_tiles(self, cord):
        nears = [(cord+near_cord).get()  for near_cord in near_cords]
        return [self.map[i][j] for i,j in nears]

    def get_voxel(self, cord):
        assert isinstance(cord, Cord)
        return self._voxels[cord].values()

    def get_near_voxels(self, cord):
        nears = [cord+near_cord for near_cord in near_cords]
        return [self._voxels[cord].values() for cord in nears]
    

    def get_free_cords(self, chunk_cord):
        assert isinstance(chunk_cord, ChunkCord)

        for cord in chunk_cord:
            print cord
            if not self._voxels[cord]:
                yield cord
    
    
    

    
    
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



    def set_activity(self):
        print ('set_activity')
        self.game.add_active_location(self)
    
    def unset_activity(self):
        print ('unset_activity')
        self.game.remove_active_location(self)



    def create_chunks(self):
        "создает локации"
        n = self.chunk_number
        cords = [ChunkCord(i,j) for i in xrange(n) for j in xrange(n)]
        self._chunks = {cord: Chunk(self, cord) for cord in cords}

        main_chunk_cord = ChunkCord(n/2, n/2)
        self.main_chunk = self._chunks[main_chunk_cord]

    def create_chunk_links(self):
        "создает ссылки в локациях"
        for chunk in self._chunks.values():
            chunk.create_links()

    def create_voxels(self):
        _range = range(self.size)
        self._voxels = {Cord(i,j): {} for i in _range for j in _range}

    def start(self):
        result = self.load_objects()
        if not result:
            self.generate_func(self)
            self.flush_genaration_data()

        number = len(self._players)
        print ('Location "%s" with %s objects has been started' % (self.name, number))


                
    
    

