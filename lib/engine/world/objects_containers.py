#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from types import ClassType

from engine.enginelib.meta import ActiveState


class ObjectContainer:
    proxy_list = ()

    def __init__(self):
        self.__forproxy__ = {p_type:p_type.__name__ for p_type in self.proxy_list}
        self.proxy_dicts = {type_name : {} for type_name in self.__forproxy__.values()}
        self.new_players = False

    def add_proxy(self, player):
        name = player.name

        for p_type, type_name in self.__forproxy__.items():
            if isinstance(player, p_type):
                self.proxy_dicts[type_name][name] = player

        self.new_players = True
        

    def remove_proxy(self, player):
        name = player.name

        for type_name in self.proxy_dicts:
            if name in self.proxy_dicts[type_name]:
                del self.proxy_dicts[type_name][name]
        self.new_players = True


    def get_list_all(self, *type_filter):
        "выдает список всех игроков в локации и соседних локациях"
        if not type_filter:
            players = sum([(chunk.players.values()) for chunk in self.nears], self.players.values())
            return players
        else:
            type_filter = list(type_filter)
            filter_type = type_filter.pop()

            assert isinstance(filter_type, ClassType)
            filter_type = filter_type.__name__

            assert filter_type in self.proxy_dicts
            
            start = self.proxy_dicts[filter_type].values()
            result = sum([chunk.proxy_dicts[filter_type].values() for chunk in self.nears], start)
            
            if not type_filter:
                return result
                
            else:
                return [player for player in result if isinstance(player, tuple(type_filter))]


    def get_list(self, *type_filter):
        if not type_filter:
            return self.players.values()

        else:
            type_filter = list(type_filter)
            filter_type = type_filter.pop()

            assert isinstance(filter_type, ClassType)
            filter_type = filter_type.__name__

            assert filter_type in self.proxy_dicts

            result = self.proxy_dicts[filter_type].values()

            if not type_filter:
                return result

            else:
                return [player for player in result if isinstance(player, tuple(type_filter))]

    def check_players(self):
        "проверяет изменился ли список объекто в локации и соседних локациях"
        if self.new_players:
            return True
        for chunk in self.nears:
            if chunk.new_players:
                return True
        return False

    def complete_round(self):
        self.new_players = False


class ActivityContainer:
    "функционал локации для работы с ее активностью"
    def __init__(self):
        self.primary_activity = 0
        self.slavery_activity = 0


    def add_activity(self, player):
        if isinstance(player, ActiveState):
            self.set_primary_activity()

    def remove_activity(self, player):
        if isinstance(player, ActiveState):
            self.unset_primary_activity()

 

    def unset_primary_activity(self):
        self.primary_activity-=1
        if self.primary_activity<=0:
            [chunk.unset_slavery_activity() for chunk in self.nears]
            if self.slavery_activity==0:
                self.unset_activity()
    
    def set_primary_activity(self):
        self.primary_activity+=1
        if self.primary_activity==1:
            [chunk.set_slavery_activity() for chunk in self.nears]
            
            if self.slavery_activity<=0:
                self.set_activity()
        

    def unset_slavery_activity(self):
        self.slavery_activity -= 1
        
        if self.primary_activity<=0 and self.slavery_activity==0:
            self.unset_activity()
    
    def set_slavery_activity(self):
        self.slavery_activity += 1
        
        if self.primary_activity<=0 and self.slavery_activity==1:
            self.set_activity()
    
    
    def set_activity(self):
        self.world.active_chunks[self.cord.get()] = self
    
    def unset_activity(self):
        key = self.cord.get()
        if key in self.world.active_chunks:
            del self.world.active_chunks[key]
        else:
            print('key error', key)