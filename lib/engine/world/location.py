#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *
xrange = range


from engine.mathlib import Cord, Position, ChunkCord


from engine.world._location.persistence import PersistentLocation
from engine.world._location.choiser import ChoiserMixin
from engine.world._location.location_math import LocationMath

from engine.world.objects_containers import ActivityContainer, near_cords

from engine.enginelib.meta import Container, Guided, HierarchySubject



from weakref import proxy, ProxyType
from collections import defaultdict



class Location(PersistentLocation, ActivityContainer, LocationMath, ChoiserMixin):
    "базовый класс карты"
    monster_count = 0
    nears = []
    
    def __init__(self, _game, name):
        PersistentLocation.__init__(self, name)
        ActivityContainer.__init__(self)
        ChoiserMixin.mixin(self)

        self.name = name
        
        
        self.teleports = [Cord(self.size/2, self.size/2)]
        
        self.chunk_number = int(self.size/CHUNK_SIZE +1)
        
        
        self._players = {}
        
        self._chunks = {}
        self.active_chunks = {}
        
        self.create_chunks()
        self.create_chunk_links()
        self.create_voxels()
        self.generate_free_cords()


        

    def new_object(self, player, chunk = None, position = None):
        assert not (chunk and position), 'chunk and position conflict %s %s' % (chunk, position)
        assert chunk is None or self.is_valid_chunk(chunk), chunk
        assert position is None or self.is_valid_position(position), position

        
        
        if isinstance(player, Guided):  print ('\n location.new_object %s' % player)
        game._new_object(player)
        
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

        game._remove_object(player)

    def add_to_voxel(self, player, cord):
        assert isinstance(cord, Cord)
        assert not hasattr(player, 'voxel')

        voxel = self._voxels[cord]
        voxel[player.name] = player

        player.voxel = voxel
        player.cord = cord

        player.cord_changed = True

        chunk_cord = cord.to_chunk()

        if self.generation:
            if cord in self._free_cords[chunk_cord]:
                self._free_cords[chunk_cord].remove(cord)

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


    def change_location(self, player, location_name):
        game.change_location(player, location_name)



          


    def get_guided_list(self, name):
        return game.get_guided_list(name)

    def is_guided_changed(self):
        return game.guided_changed

    def change_guided(self):
        game.guided_changed = True

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



    def set_activity(self):
        print ('location set_activity')
        game.add_active_location(self)
    
    def unset_activity(self):
        print ('location unset_activity')
        game.remove_active_location(self)



    

    

    def start(self):
        result = self.load_objects()
        if not result:
            self.generate_func(self)
        self.flush_genaration_data()

        number = len(self._players)
        print ('Location "%s" with %s objects has been started' % (self.name, number))



##кольцевая зависимость
from engine.world.singleton import game