#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from weakref import proxy, ProxyType
from collections import Counter


from engine.enginelib.meta import ActiveState
from engine.mathlib import Cord, Position, ChunkCord



#список инкременаторов к индексу на соседние локации
nears =    ((-1,1),(0,1),(1,1),
            (-1,0),      (1,0),
            (-1,-1),(0,-1),(1,-1))


near_cords = [Cord(i,j) for i,j in nears]
near_chunk_cords = [ChunkCord(i,j) for i,j in nears]


class ObjectContainer(object):
    "контейнер для игровых объектов, отмечающий изменения игроков и хранящий прокси-списки по типам объектов"
    proxy_list = ()
    __counter = Counter()

    def __init__(self):
        for p_type in self.proxy_list:
            assert isinstance(p_type, type)
        self.__forproxy__ = {p_type:p_type.__name__ for p_type in self.proxy_list}
        self.__proxy_dicts = {type_name : {} for type_name in self.__forproxy__.values()}
        self.new_players = False

    def set_new_players(self):
        self.new_players = True

    def add_proxy(self, player):
        assert isinstance(player, ProxyType)
        
        name = player.name

        for p_type, type_name in self.__forproxy__.items():
            if isinstance(player, p_type):
                self.__proxy_dicts[type_name][name] = player

        self.new_players = True
        

    def remove_proxy(self, player):
        name = player.name

        
        for p_type, type_name in self.__forproxy__.items():
            if isinstance(player, p_type):
                del self.__proxy_dicts[type_name][name]
        self.new_players = True


    def get_list(self, *type_filter):
        return self._get_list(False, *type_filter)

    def get_list_all(self, *type_filter):
        return self._get_list(True, *type_filter)

    def _get_list(self, all, *type_filter):
        self.__counter['ALL']+=1
        if not type_filter:
            self.__counter['None']+=1
            if all:
                return sum([list(chunk.players.values()) for chunk in self.nears], list(self.players.values()))
            else:
                return list(self.players.values())

        else:

            type_filter = list(type_filter)
            filter_type = type_filter.pop()

            assert isinstance(filter_type, type)

            filter_type = filter_type.__name__

            self.__counter[filter_type]+=1

            assert filter_type in self.__proxy_dicts

            if all:
                start = list(self.__proxy_dicts[filter_type].values())
                result = sum([list(chunk.__proxy_dicts[filter_type].values()) for chunk in self.nears], start)
            else:
                result = list(self.__proxy_dicts[filter_type].values())

            if not type_filter:
                return result

            else:
                return [player for player in result if isinstance(player, tuple(type_filter))]


    def check_players(self):
        "проверяет изменился ли список объекто в локации и соседних локациях"
        if self.new_players:
            return True
        for container in self.nears:
            if container.new_players:
                return True
        return False

    def complete_round(self):
        self.new_players = False




class ActivityContainer(object):
    "функционал локации для работы с ее активностью"
    def __init__(self):
        assert hasattr(self, 'nears')
        self.primary_activity = 0
        self.slavery_activity = 0

    def _assertion(self):
        return self.primary_activity >= 0 and self.slavery_activity >= 0 


    def add_activity(self, player):
        assert self._assertion()

        if isinstance(player, ActiveState):
            self.set_primary_activity()

    def remove_activity(self, player):
        assert self._assertion()
        
        if isinstance(player, ActiveState):
            self.unset_primary_activity()

 

    def unset_primary_activity(self):
        assert self._assertion()

        self.primary_activity-=1
        if self.primary_activity==0:
            [chunk.unset_slavery_activity() for chunk in self.nears]
            if self.slavery_activity==0:
                self.unset_activity()
    
    def set_primary_activity(self):
        assert self._assertion()

        self.primary_activity+=1
        if self.primary_activity==1:
            [chunk.set_slavery_activity() for chunk in self.nears]
            
            if self.slavery_activity==0:
                self.set_activity()

        

    def unset_slavery_activity(self):
        assert self._assertion()

        self.slavery_activity -= 1
        
        if self.primary_activity==0 and self.slavery_activity==0:
            self.unset_activity()
    
    def set_slavery_activity(self):
        assert self._assertion()
        
        self.slavery_activity += 1
        
        if self.primary_activity==0 and self.slavery_activity==1:
            self.set_activity()
    
    
    def set_activity(self):
        pass
    
    def unset_activity(self):
        pass

    def __del__(self):
        pass