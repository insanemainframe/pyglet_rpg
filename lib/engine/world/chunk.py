#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from weakref import proxy

from share.point import Point
from engine.world.objects_containers import ActivityContainer, ObjectContainer
from engine.enginelib.meta import Solid, Updatable, Deadly, DiplomacySubject
from engine.gameobjects.teleports import Teleport


#список инкременаторов к индексу на соседние локации
near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]


class Chunk(ObjectContainer, ActivityContainer):
    "функционал локации для работы с объектами"
    proxy_list = (Solid, Updatable, Deadly, DiplomacySubject, Teleport)
    def __init__(self, world, i,j):
        self.world = world
        self.i, self.j = i,j
        self.cord = Point(i,j)
        
        ObjectContainer.__init__(self)
        ActivityContainer.__init__(self)
        
        self.nears = []

        self.players = {}
        self.remove_list = {}

        self.new_events = False
        self.map_changed = False

        base_i, base_j = i*CHUNK_SIZE, j*CHUNK_SIZE
        self.tile_keys = [(base_i+I, base_j+J) for I in range(CHUNK_SIZE) for J in range(CHUNK_SIZE)
                         if 0<base_i+I<self.world.size and 0<base_j+J < self.world.size] 

    def set_activity(self):
        self.world.add_active_chunk(self)
    
    def unset_activity(self):
        self.world.remove_active_chunk(self)

    def set_map_changed(self):
        self.map_changed = True
        
    
    def add_object(self, player):
        "добавляет ссылку на игрока"
        self.add_activity(player)
        self.add_proxy(player)
        self.players[player.name] = proxy(player)

    
    def pop_object(self, player):
        "удаляет ссылку из списка игроков"
        name = player.name

        if name in self.players:
            self.remove_activity(player)
            self.remove_proxy(player)
            del self.players[player.name]

            if name in self.remove_list:
                del self.remove_list[name]


    def remove_object(self, name, force = False):
        "удаляет игрока, если его метод remove возвращает true"
        if name in self.players:
            player = self.players[name]

            result = player.remove()
            
            if result or force:
                self.pop_object(player)
                self.world.game.remove_object(player)

            else:
                player.handle_remove()
        
    
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
        "удаляет игроков отмеченных для удаления в списке remove_list"
        if self.remove_list:
            for name, force in self.remove_list.items():
                self.remove_object(name, force)

            self.remove_list.clear()
    

  
    def add_to_remove(self, player, force):
        "добавляет статический объект в список для удаления"
        name = player.name
        self.remove_list[name] = force
    
    

        
    def create_links(self):
        "создает сслыки на соседние локации"
        for i,j in near_cords:
            try:
                near_chunk = self.world.chunks[self.i+i][self.j+j]
            except IndexError:
                pass
            else:
                self.nears.append(near_chunk)
        
    def update(self):
        "очистка объекьтов"
        self.clear_players()
    
    def complete_round(self):
        self.remove_list.clear()
        
        ObjectContainer.complete_round(self)
        self.map_changed = False
        self.new_events = False



