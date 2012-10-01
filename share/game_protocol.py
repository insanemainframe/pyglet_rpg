#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from share.mathlib import Point

#########################################################################
class GameProtocol:
    pass
#общие методы классов протоколов

class Events:
    #name, object_type, action, args=()
    def pack_events(self, events):
        return [event.get_tuple() for event in events]
    
    def unpack_events(self, events):
        return [(name, object_type,  Point(x,y), action, args)
            for (name, object_type, (x,y), action, args) in events]

class Observed:
    def pack_observed(self, observed):
        return [(i,j) for (i,j) in observed]
    def unpack_observed(self, observed):
        return [(i,j) for (i,j) in observed]

class Land:
    def pack_land(self, land):
        return [point.get()+(tilename,) for point, tilename in land]
    def unpack_land(self, land):
        return [(Point(x,y),tilename) for x,y, tilename in land]

class StaticObjects(Events):
    def pack_static_objects(self, static_objects):
        return dict([(name, (o_type, position.get())) for name, (o_type, position) in static_objects.items()])
        
    def unpack_static_objects(self, static_objects):
        return dict([(name, (o_type, Point(x,y))) for name, (o_type, (x,y)) in static_objects.items()])
    



#########################################################################
#классы протоколов

#инициализация
class ServerAccept(GameProtocol, Events, Land, Observed, StaticObjects):
    "ответ сервера - инициализация клиента"
    def pack(self, world_size, position, land, observed, events, static_objects, static_objects_events):
        
        x,y = position.get()
        land = self.pack_land(land)
        observed = self.pack_observed(observed)
        events = self.pack_events(events)
        static_objects = self.pack_static_objects(static_objects)
        static_objects_events = self.pack_events(static_objects_events)
        
        return (world_size, (x,y), land, observed, events, static_objects, static_objects_events)

    def unpack(self, world_size, (x,y), land, observed, events, static_objects, static_objects_events):
        
        position = Point(x,y)
        land = self.unpack_land(land)
        observed =  self.unpack_observed(observed)
        events = self.unpack_events(events)
        static_objects = self.unpack_static_objects(static_objects)
        static_objects_events = self.unpack_events(static_objects_events)
        
        return world_size, position, land, observed, events, static_objects, static_objects_events

#
#запрос на иницализацию
class ClientAccept(GameProtocol):
    "запрос клиента"
    @staticmethod
    def pack_client_accept(name):
        return name
    
    @staticmethod
    def unpack_client_accept(name):
        return name
#обзор
class Look(GameProtocol, Events, Land, Observed, StaticObjects):
    def pack(self, move_vector, land, observed, events, static_objects, static_objects_events):
        
        move_vector = move_vector.get()
        land = self.pack_land(land)
        observed =  self.pack_observed(observed)
        events = self.pack_events(events)
        static_objects = self.pack_static_objects(static_objects)
        static_objects_events = self.pack_events(static_objects_events)
        
        return move_vector, land, observed, events, static_objects, static_objects_events

    def unpack(self, (x,y), land, observed, events, static_objects, static_objects_events):
        
        move_vector = Point(x,y)
        land =  self.unpack_land(land)
        observed =  self.unpack_observed(observed)
        events = self.unpack_events(events)
        static_objects = self.unpack_static_objects(static_objects)
        static_objects_events = self.unpack_events(static_objects_events)
        
        return move_vector, land, observed, events, static_objects, static_objects_events

#статы игрока
class PlayerStats(GameProtocol):
    @staticmethod
    def pack(hp, hp_value, speed, damage, gold, kills, death_counter, skills):
        return hp, hp_value, speed, damage, gold, kills, death_counter, skills
    @staticmethod
    def unpack(hp, hp_value, speed, damage, gold, kills, death_counter, skills):
        return hp, hp_value, speed, damage, gold, kills, death_counter, skills
    

#передвижение
class Move(GameProtocol):
    @staticmethod
    def pack(vector):
        return vector.get()
    
    @staticmethod
    def unpack(x,y):
        return [Point(x,y)]

#стрельба
class Strike(GameProtocol):
    @staticmethod
    def pack(vector):
        return vector.get()
    @staticmethod
    def unpack(x,y):
        return [Point(x,y)]
#
class Skill(GameProtocol):
    @staticmethod
    def pack(a=None):
        return []
    @staticmethod
    def unpack(a=None):
        return []
#РЕСПАВН
class Respawn(GameProtocol):
    @staticmethod
    def pack(position):
        return position.get()
    @staticmethod
    def unpack(x,y):
        return Point(x,y)
#
#словарь хэндлеров на действия
_method_handlers = {'move': Move(),
                'ball': Strike(),
                'look' : Look(),
                'server_accept': ServerAccept(),
                'respawn': Respawn()}
                
                










