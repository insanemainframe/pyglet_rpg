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
    @classmethod
    def pack_events(cls, events):
        return [event.get_tuple() for event in events]
        
    @classmethod
    def unpack_events(cls, events):
        return [(name, object_type,  Point(x,y), action, args)
            for (name, object_type, (x,y), action, args) in events]


    
        

#########################################################################
#классы протоколов

#######################################################################
#ответы сервера
#инициализация
class NewWorld(GameProtocol):
    "ответ сервера - инициализация клиента"
    def __init__(self, world_size, position, background):
        self.world_size = world_size
        self.position = position
        self.background = background
    
    def pack(self):
        x,y = self.position.get()
        return self.world_size, (x,y), self.background
    
    @classmethod
    def unpack(cls, world_size, (x,y), background):
        position = Point(x,y)
        return world_size, position, background

#

#обзор
class MoveCamera(GameProtocol):
    def __init__(self, move_vector):
        self.move_vector = move_vector
    
    def pack(self):
        x,y = self.move_vector.get()
        return [x,y]
        
    @classmethod
    def unpack(cls, x,y):
        move_vector = Point(x,y)
        return move_vector

class LookLand(GameProtocol):
    def __init__(self, land, observed):
        self.land = land
        self.observed = observed
    
    def pack(self):
        land = [point.get()+(tilename,) for point, tilename in self.land]
        observed =  [(i,j) for (i,j) in self.observed]
        
        return land, observed
    
    @classmethod
    def unpack(cls,land,observed):
        land =  [(Point(x,y),tilename) for x,y, tilename in land]
        observed =  [(i,j) for (i,j) in observed]

        return land, observed

class LookEvents(GameProtocol, Events):
    def __init__(self, events):
        self.events = events
        
    def pack(self):
        events = self.pack_events(self.events)
        return [events]
    
    @classmethod
    def unpack(cls, events):
        events = cls.unpack_events(events)
        return events

class LookPlayers(GameProtocol):
    def __init__(self, players):
        self.players = players
    
    def pack(self):
        players = dict([(gid, (name, o_type, position.get(), args))
            for gid, (name, o_type, position, args) in self.players.items()])
        return [players]
    
    @classmethod
    def unpack(cls, players):
        players = dict([(gid, (name, o_type, Point(x,y), args))
            for gid, (name, o_type, (x,y), args) in players.items()])
        return players

class LookStaticObjects(LookPlayers):
    pass


class LookStaticEvents(GameProtocol, Events):
    def __init__(self, static_objects_events):
        self.static_objects_events = static_objects_events
        
    def pack(self):
        static_objects_events = self.pack_events(self.static_objects_events)
        return [static_objects_events]
    
    @classmethod
    def unpack(cls, static_objects_events):
        static_objects_events = cls.unpack_events(static_objects_events)
        return static_objects_events

#статы игрока
class PlayerStats(GameProtocol):
    def __init__(self, hp, hp_value, speed, damage, gold, kills, death_counter, skills, invisible):
        self.hp = hp
        self.hp_value = hp_value
        self.speed = speed
        self.damage = damage
        self.gold = gold
        self. kills = kills
        self.death_counter = death_counter
        self.skills = skills
        self.invisible = invisible
        
    def pack(self):
        return (self.hp, self.hp_value, self.speed, self.damage,
                self.gold, self.kills, self.death_counter,
                self.skills, self.invisible)
    
    @classmethod
    def unpack(cls, hp, hp_value, speed, damage, gold, kills, death_counter, skills, invisible):
        return hp, hp_value, speed, damage, gold, kills, death_counter, skills, invisible

#РЕСПАВН
class Respawn(GameProtocol):
    def __init__(self, position):
        self.position = position
    
    def pack(self):
        return self.position.get()
    
    @classmethod
    def unpack(cls, x,y):
        return Point(x,y)
        
#######################################################################
#запросы клиента

#передвижение
class Move(GameProtocol):
    def __init__(self, vector):
        self.vector = vector
    
    def pack(self):
        return self.vector.get()
    
    @classmethod
    def unpack(cls, x,y):
        return [Point(x,y)]

#стрельба
class Strike(GameProtocol):
    def __init__(self, vector):
        self.vector = vector
    
    def pack(self):
        return self.vector.get()
    
    @classmethod
    def unpack(cls, x,y):
        return [Point(x,y)]
#
class Skill(GameProtocol):
    def __init__(self):
        pass
    
    def pack(a=None):
        return []
    
    @classmethod
    def unpack(cls, a=None):
        return []

                










