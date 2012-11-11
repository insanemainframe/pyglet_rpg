#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.mathlib import Cord, Position, ChunkCord


from weakref import proxy, ProxyType

from engine.world.voxel import Voxel
from engine.world.objects_containers import ActivityContainer, ObjectContainer, near_chunk_cords


from engine.enginelib.meta import Solid, Updatable, DiplomacySubject, Guided
from engine.enginelib.mutable import MutableObject

from engine.enginelib.units_lib import Unit
from engine.gameobjects.teleports import Teleport




class Chunk(ObjectContainer, ActivityContainer):
    "функционал локации для работы с объектами"
    proxy_list = (MutableObject, Solid, Updatable, Unit, Teleport)
    def __init__(self, location, cord):
        self.location = location
        self.cord = cord
        self.base_cord = cord*TILESIZE

        
        ObjectContainer.__init__(self)
        ActivityContainer.__init__(self)
        
        self.nears = []

        self._players = {}
        self.delay_args = {}

        self.new_events = False
        self.map_changed = False

        

        self.create_voxels()
        self.free_cords = self._voxels.keys()[:]
   
        

    def __getitem__(self, cord):
        return self._voxels[cord]

    def __contains__(self, cord):
        return cord in self._voxels


    def create_voxels(self):
        voxels_cords  = [self.cord.to_cord() + Cord(i,j)
                        for i in range(CHUNK_SIZE)
                        for j in range(CHUNK_SIZE)]
                        
        self._voxels = {cord: Voxel(self, cord) for cord in voxels_cords if self.location.is_valid_cord(cord)}

    def link_voxels(self):
        [voxel.create_links() for voxel in self._voxels.values()]


        

    def change_position(self, player, new_position):
        assert isinstance(player, ProxyType)
        assert isinstance(new_position, Position)


        


        if self.location.is_valid_position(new_position):
            player._prev_position = player._position
            player._position  = new_position
            player.position_changed = True

            new_cord = new_position.to_cord()

            if player.cord!=new_cord:
                new_chunk = new_position.to_chunk()

                if new_chunk!=player.chunk.cord:
                    self.location.change_chunk(player, new_chunk, new_position)
                else:
                    prev_voxel = player.voxel
                    prev_voxel.remove(player)

                    new_voxel = self[new_cord]
                    new_voxel.append(player)

                    player.cord = new_cord
                    player.cord_changed = True
                        
                    
                



        
    
    def add_object(self, player, position):
        "добавляет ссылку на игрока"
        assert isinstance(player, ProxyType)
        assert not hasattr(player, 'chunk')

        if isinstance(player, Guided):  print ('chunk.add_object', player)

        player.chunk = proxy(self)
        
        self.add_activity(player)
        self.add_proxy(player)
        self._players[player.name] = player

        cord = position.to_cord()
        voxel = self[cord]
        voxel.append(player)

        if cord in self.free_cords:
            self.free_cords.remove(cord)

        player.set_position(position)

    
    def pop_object(self, player):
        "удаляет ссылку из списка игроков"
        assert player.name in self._players

        # if isinstance(player, Guided):  print ('chunk.pop_object', player)
        
        name = player.name
        
            

        self.remove_activity(player)
        self.remove_proxy(player)

        voxel = player.voxel
        voxel.remove(player)

        del self._players[player.name]
        del player.chunk


    def set_event(self):
        self.new_events = True
        
    
    def check_events(self):
        if self.new_events:
            return True
        for chunk in self.nears:
            if chunk.new_events:
                return True
        
        return False

    def get_nears(self):
        return self.nears


    def get_free_cords(self):
        #return self.free_cords
        return self._voxels.keys()


    def clear_players(self):
        "удаляет игроков отмеченных для удаления"
        remove_list = [player for player in self._players.values() if player._REMOVE]
            
        for player in remove_list:
            self.location.remove_object(player)
    
        
    def create_links(self,):
        "создает сслыки на соседние локации"
        for cord in near_chunk_cords:
            try:
                near_chunk = self.location[self.cord + cord]
            except KeyError as error:
                #print 'KeyError', error
                pass
            else:
                self.nears.append(near_chunk)
        self.link_voxels()
        
    def update(self):
        "очистка объекьтов"
        self.clear_players()
    
    def complete_round(self):        
        ObjectContainer.complete_round(self)
        self.map_changed = False
        self.new_events = False
        self.delay_args.clear()

    def set_activity(self):
        self.location.add_active_chunk(self)
    
    def unset_activity(self):
        self.location.remove_active_chunk(self)


