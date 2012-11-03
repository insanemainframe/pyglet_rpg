#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from weakref import proxy, ProxyType

from share.point import Point
from engine.world.objects_containers import ActivityContainer, ObjectContainer
from engine.enginelib.meta import Solid, Updatable, Deadly, DiplomacySubject
from engine.enginelib.units_lib import Unit
from engine.gameobjects.teleports import Teleport


#список инкременаторов к индексу на соседние локации
near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]

class Chunk(ObjectContainer, ActivityContainer):
    "функционал локации для работы с объектами"
    proxy_list = (Solid, Updatable, Deadly, Unit, Teleport)
    def __init__(self, location, i,j):
        self.location = location
        self.i, self.j = i,j
        self.cord = Point(i,j)
        
        ObjectContainer.__init__(self)
        ActivityContainer.__init__(self)
        
        self.nears = []

        self._players = {}
        self.delay_args = {}

        self.new_events = False
        self.map_changed = False

        base_i, base_j = i*CHUNK_SIZE, j*CHUNK_SIZE
        self.tile_keys = [(base_i+I, base_j+J) for I in range(CHUNK_SIZE) for J in range(CHUNK_SIZE)
                         if 0<base_i+I<self.location.size and 0<base_j+J < self.location.size] 

    def set_activity(self):
        self.location.add_active_chunk(self)
    
    def unset_activity(self):
        self.location.remove_active_chunk(self)

    def set_map_changed(self):
        self.map_changed = True
        
    
    def add_object(self, player):
        "добавляет ссылку на игрока"
        assert isinstance(player, ProxyType)

        self.add_activity(player)
        self.add_proxy(player)
        self._players[player.name] = player

    
    def pop_object(self, player, delay_args = False):
        "удаляет ссылку из списка игроков"
        name = player.name

        if delay_args:
            self.delay_args[player.gid] = delay_args

        if name in self._players:
            self.remove_activity(player)
            self.remove_proxy(player)
            del self._players[player.name]



        
    
    def set_event(self):
        self.new_events = True
        
    
    def check_events(self):
        if self.new_events:
            return True
        for chunk in self.nears:
            if chunk.new_events:
                return True
        
        return False

    
    


    def clear_players(self):
        "удаляет игроков отмеченных для удаления"
        remove_list = [player for player in self._players.values() if player._REMOVE]
            
        for player in remove_list:
            self.location.game.remove_object(player)
    
        
    def create_links(self):
        "создает сслыки на соседние локации"
        for i,j in near_cords:
            try:
                near_chunk = self.location.chunks[self.i+i][self.j+j]
            except IndexError:
                pass
            else:
                self.nears.append(near_chunk)
        
    def update(self):
        "очистка объекьтов"
        self.clear_players()
    
    def complete_round(self):        
        ObjectContainer.complete_round(self)
        self.map_changed = False
        self.new_events = False
        self.delay_args.clear()


    def debug(self):
        if DEBUG_WEAK_REFS:
            for ref in self._players.values():
                try:
                    ref.__doc__
                except ReferenceError as error:
                    print('%s: chunk %s' % (error,self.cord))
                    raw_input('Debug:')

