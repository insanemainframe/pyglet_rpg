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

#######################################################################
#ответы сервера
#инициализация
class ServerAccept(GameProtocol):
    "ответ сервера - инициализация клиента"
    def pack(self, world_size, position):
        x,y = position.get()
        return world_size, (x,y)

    def unpack(self, world_size, (x,y)):
        position = Point(x,y)
        return world_size, position

#

#обзор
class MoveCamera(GameProtocol):
    @staticmethod
    def pack(move_vector):
        x,y = move_vector.get()
        return [x,y]
    @staticmethod
    def unpack(x,y):
        move_vector = Point(x,y)
        return move_vector

class LookLand(GameProtocol,Land, Observed):
    def pack(self, land, observed):
        land = self.pack_land(land)
        observed =  self.pack_observed(observed)
        
        return land, observed

    def unpack(self,land,observed):
        land =  self.unpack_land(land)
        observed =  self.unpack_observed(observed)

        
        return land, observed

class LookObjects(GameProtocol, Events):
    def pack(self, events):
        events = self.pack_events(events)
        return [events]
    
    def unpack(self, events):
        events = self.unpack_events(events)
        return events

class LookStatic(GameProtocol, StaticObjects, Events):
    def pack(self, static_objects, static_objects_events):
        static_objects = self.pack_static_objects(static_objects)
        static_objects_events = self.pack_events(static_objects_events)
        return static_objects, static_objects_events
    
    def unpack(self, static_objects, static_objects_events):
        static_objects = self.unpack_static_objects(static_objects)
        static_objects_events = self.unpack_events(static_objects_events)
        return static_objects, static_objects_events

#статы игрока
class PlayerStats(GameProtocol):
    @staticmethod
    def pack(hp, hp_value, speed, damage, gold, kills, death_counter, skills):
        return hp, hp_value, speed, damage, gold, kills, death_counter, skills
    @staticmethod
    def unpack(hp, hp_value, speed, damage, gold, kills, death_counter, skills):
        return hp, hp_value, speed, damage, gold, kills, death_counter, skills

#РЕСПАВН
class Respawn(GameProtocol):
    @staticmethod
    def pack(position):
        return position.get()
    @staticmethod
    def unpack(x,y):
        return Point(x,y)
        
#######################################################################
#запросы клиента

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

#запрос на иницализацию(на будущее)
class ClientAccept(GameProtocol):
    "запрос клиента"
    @staticmethod
    def pack_client_accept(name):
        return name
    
    @staticmethod
    def unpack_client_accept(name):
        return name
                
                










