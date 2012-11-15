#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.mathlib import Cord, Position, ChunkCord


from weakref import proxy, ProxyType

from engine.world.objects_containers import ActivityContainer, ObjectContainer, near_chunk_cords


from engine.enginelib.meta import Solid, Updatable, DiplomacySubject, Guided
from engine.enginelib.mutable import MutableObject

from engine.enginelib.units_lib import Unit, MetaMonster
from engine.gameobjects.teleports import Teleport




class Chunk(ObjectContainer, ActivityContainer):
    "функционал локации для работы с объектами"
    proxy_list = (MutableObject, Solid, Updatable, Unit, Teleport)
    def __init__(self, location, cord):
        self.location = location
        self.cord = cord
        self.base_cord = cord*TILESIZE

        self.nears = []
        
        ObjectContainer.__init__(self)
        ActivityContainer.__init__(self)
        
        

        self._players = {}
        self.delay_args = {}

        self.new_events = False
        self._remove_list = set()

        self.__protected = False

    
    def set_protected(self):
        self.__protected = True


        
    def change_position(self, player, new_position):
        assert isinstance(player, ProxyType)
        assert isinstance(new_position, Position)



        if self.location.is_valid_position(new_position):
            player._prev_position = player._position
            player._position  = new_position
            player.position_changed = True

            new_cord = new_position.to_cord()

            if player.cord!=new_cord:

                self.location.change_voxel(player, new_cord)

                new_chunk_cord = new_position.to_chunk()

                if new_chunk_cord!=player.chunk.cord:
                    self.location.change_chunk(player, new_chunk_cord, new_position)

                        
                    
                



        
    
    def add_object(self, player, position):
        "добавляет ссылку на игрока"
        assert isinstance(player, ProxyType)
        assert not hasattr(player, 'chunk')

        if isinstance(player, Guided):  print ('chunk.add_object', player)

        if self.__protected and isinstance(player, MetaMoster):
            return False

        else:
            player.chunk = proxy(self)
            
            self.add_activity(player)
            self.add_proxy(player)
            self._players[player.name] = player

            player.set_position(position)
            return True

    
    def pop_object(self, player):
        "удаляет ссылку из списка игроков"
        assert player.name in self._players

        # if isinstance(player, Guided):  print ('chunk.pop_object', player)
        
        name = player.name
        
            

        self.remove_activity(player)
        self.remove_proxy(player)

        if name in self._remove_list:
            self._remove_list.remove(name)

        del self._players[player.name]
        del player.chunk

    def add_to_remove(self, name):
        self._remove_list.add(name)

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




    
        
    def create_links(self,):
        "создает сслыки на соседние локации"
        for chunk_cord in near_chunk_cords:
            if self.location.is_valid_chunk(self.cord + chunk_cord):
                near_chunk = self.location.get_chunk(self.cord + chunk_cord)
                self.nears.append(near_chunk)
        
    def update(self):
        "очистка объекьтов"            
        for name in self._remove_list.copy():
            assert name in self._players, self._remove_list
            player = self._players[name]
            self.location.remove_object(player)

        self._remove_list.clear()
    
    def complete_round(self):        
        ObjectContainer.complete_round(self)
        self.map_changed = False
        self.new_events = False
        self.delay_args.clear()

    def set_activity(self):
        self.location.add_active_chunk(self)
    
    def unset_activity(self):
        self.location.remove_active_chunk(self)


