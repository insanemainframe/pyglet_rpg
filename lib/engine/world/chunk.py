#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from weakref import proxy, ProxyType

from share.point import Point
from engine.world.objects_containers import ActivityContainer, ObjectContainer
from engine.enginelib.meta import Solid, Updatable, Breakable, DiplomacySubject, Guided
from engine.enginelib.units_lib import Unit
from engine.gameobjects.teleports import Teleport


#список инкременаторов к индексу на соседние локации
near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]

class Chunk(ObjectContainer, ActivityContainer):
    "функционал локации для работы с объектами"
    proxy_list = (Solid, Updatable, Breakable, Unit, Teleport)
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

    def change_position(self, player, new_position):
        assert isinstance(player, ProxyType)
        assert isinstance(new_position, Point)

        prev_position = player._position

        new_cord = new_position/TILESIZE

        if self.location.is_valid_position(new_position):
            player._prev_position = player._position
            player._position  = new_position
            player.position_changed = True

            new_chunk = self.location.get_chunk_cord(new_position)

            if new_chunk!=player.chunk.cord:
                self.location.change_chunk(player, new_chunk)

            if player.cord!=new_cord:
                self.location.change_cord(player, new_cord)
                    
            
  
                


    def set_activity(self):
        self.location.add_active_chunk(self)
    
    def unset_activity(self):
        self.location.remove_active_chunk(self)

    def set_map_changed(self):
        self.map_changed = True
        
    
    def add_object(self, player):
        "добавляет ссылку на игрока"
        assert isinstance(player, ProxyType)
        assert not hasattr(player, 'chunk')

        # if isinstance(player, Guided):  print ('chunk.add_object', player)

        player.chunk = proxy(self)
        
        self.add_activity(player)
        self.add_proxy(player)
        self._players[player.name] = player

    
    def pop_object(self, player):
        "удаляет ссылку из списка игроков"
        assert player.name in self._players

        # if isinstance(player, Guided):  print ('chunk.pop_object', player)
        
        name = player.name
        
            

        self.remove_activity(player)
        self.remove_proxy(player)

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

    


    def clear_players(self):
        "удаляет игроков отмеченных для удаления"
        remove_list = [player for player in self._players.values() if player._REMOVE]
            
        for player in remove_list:
            self.location.remove_object(player)
    
        
    def create_links(self, chunk_map):
        "создает сслыки на соседние локации"
        for i,j in near_cords:
            try:
                near_chunk = chunk_map[self.i+i][self.j+j]
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




