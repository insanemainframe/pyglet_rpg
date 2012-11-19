#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.mathlib import Cord, Position, ChunkCord


from weakref import proxy, ProxyType
from collections import defaultdict

from engine.world.objects_containers import ActivityContainer, ObjectContainer, near_chunk_cords


from engine.enginelib.meta import Solid, DiplomacySubject, Guided
from engine.enginelib.mutable import MutableObject

from engine.enginelib.units_lib import Unit, MetaMonster
from engine.gameobjects.teleports import Teleport




class Chunk(ObjectContainer, ActivityContainer):
    "функционал локации для работы с объектами"
    proxy_list = (MutableObject, Solid, Unit, Teleport)
    def __init__(self, location, cord):
        self.location = location
        self.cord = cord
        self.base_cord = cord*TILESIZE

        self.nears = []
        
        ObjectContainer.__init__(self)
        ActivityContainer.__init__(self)
        
        

        self.__players = {}
        self.__events = defaultdict(list)
        self.cords_changed = False

        self._delay_args = {}

        self._new_events = False
        self.__remove_list = set()
        self.__updaters = {}

        self.__protected = False




        
    def change_position(self, player, new_position):
        assert isinstance(player, ProxyType)
        assert isinstance(new_position, Position)

        if self.location.is_valid_position(new_position):
            
            player._prev_position = player._position
            player._position  = new_position
            player.position_changed = True

            new_cord = new_position.to_cord()

            if player.cord!=new_cord:
                self.cords_changed = True

                self.location.change_voxel(player, new_cord)

                new_chunk_cord = new_position.to_chunk()

                if new_chunk_cord!=player.chunk.cord:
                    self.location.change_chunk(player, new_chunk_cord, new_position)
        
    
    def add_object(self, player, position):
        "добавляет ссылку на игрока"
        name = player.name

        assert isinstance(player, ProxyType)
        assert not hasattr(player, 'chunk')
        assert not name in self.__players
        assert name not in self.__updaters

        player.chunk = proxy(self)
        
        self.add_activity(player)
        self.add_proxy(player)
        self.__players[name] = player

        if player._GameObject__activity>0:
            self.__updaters[name] = player

        player.set_position(position)

    
    def pop_object(self, player):
        "удаляет ссылку из списка игроков"
        name = player.name

        assert player.name in self.__players
        assert player.chunk==self

        self.remove_proxy(player)
        self.remove_activity(player)
        

        if name in self.__remove_list:
            self.__remove_list.remove(name)

        if name in self.__updaters:
            del self.__updaters[name]

        del self.__players[player.name]
        del player.chunk


    def add_to_remove(self, name):
        self.__remove_list.add(name)

    def add_delay(self, gid, action, args):
        self._delay_args[gid] = (action, args)

    def get_delay_args(self):
        return self._delay_args.items()


    def add_to_update(self, name):
        assert name in self.__players
        assert self.__players[name]._GameObject__activity>0

        # print 'add to update', name

        if name not in self.__updaters:
            self.__updaters[name] = self.__players[name]

    def pop_from_update(self, name):
        assert isinstance(name, str)
        assert self.__players[name]._GameObject__activity==0
        assert name in self.__updaters

        del self.__updaters[name]

    def add_event(self, gid, event):
        self._new_events = True
        self.__events[gid].append(event)
        
    
    def check_events(self):
        if self._new_events:
            return True
        for chunk in self.nears:
            if chunk._new_events:
                return True
        
        return False


    def get_events(self):
        return sum([chunk.__events.items() for chunk in self.nears], self.__events.items())


    def check_positions(self):
        if self.cords_changed:
            return True
        for chunk in self.nears:
            if chunk.cords_changed:
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
    
    def update(self, cur_time):
        for player in self.__updaters.values():
            if player.is_alive():
                player.update(cur_time)

    def clear(self):
        "очистка объекьтов"       
        if self.__remove_list:     
            for name in self.__remove_list.copy():
                assert name in self.__players, self.__remove_list
                player = self.__players[name]
                self.location.remove_object(player)

            self.__remove_list.clear()
    
    def complete_round(self):
        # for player in self.get_list(MutableObject):
        #         MutableObject._complete_round(player)
                
        for player in self.__updaters.values():
                player.complete_round()

        self.cords_changed = False

        self._new_events = False
        self.__events.clear()

        self._delay_args.clear()

        super(Chunk, self).complete_round()

    def set_activity(self):
        self.location.add_active_chunk(self)
    
    def unset_activity(self):
        self.location.remove_active_chunk(self)

    def __eq__(self, chunk):
        assert isinstance(chunk, Chunk)
        return self.cord==chunk.cord

    def __del__(self):
        print 'del chunk'
        super(Chunk, self).__del__()


