#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from share.mathlib import Point

#########################################################################
class GameProtocol:
    pass
#общие методы классов протоколов

class Updates:
    #name, object_type, action, args=()
    def pack_updates(self, updates):
        return [(name, object_type, position.get(), action, args)
                for uid, (name, object_type, position, action, args) in updates.items()]
    
    def unpack_updates(self, updates):
        return [(name, object_type,  Point(x,y), action, args)
            for (name, object_type, (x,y), action, args) in updates]

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

class Steps:
    def pack_steps(self, steps):
        return [(point.get(), step) for point, step in steps]
    def unpack_steps(self, steps):
        return [(Point(x,y), step) for (x,y), step in steps]


#########################################################################
#классы протоколов

#инициализация
class ServerAccept(GameProtocol, Updates, Land, Observed, Steps):
    def pack(self, data):
        world_size, position, hp, land, observed, updates, steps = data
        
        x,y = position.get()
        land = self.pack_land(land)
        observed = self.pack_observed(observed)
        updates = self.pack_updates(updates)
        steps = self.pack_steps(steps)
        
        return (world_size, (x,y), hp, land, observed, updates, steps)

    def unpack(self, data):
        world_size, (x,y), hp, land, observed, updates, steps = data
        
        position = Point(x,y)
        land = self.unpack_land(land)
        observed =  self.unpack_observed(observed)
        updates = self.unpack_updates(updates)
        steps = self.unpack_steps(steps)
        
        return world_size, position, hp, land, observed, updates, steps

#
#запрос на иницализацию
class ClientAccept(GameProtocol):
    @staticmethod
    def pack_client_accept(data):
        name = data
        return name
    
    @staticmethod
    def unpack_client_accept(data):
        name = data
        return name
#обзор
class Look(GameProtocol, Updates, Land, Observed, Steps):
    def pack(self, data):
        move_vector, hp, land, observed, updates, steps = data
        
        move_vector = move_vector.get()
        land = self.pack_land(land)
        observed =  self.pack_observed(observed)
        updates = self.pack_updates(updates)
        steps = self.pack_steps(steps)
        
        return move_vector, hp, land, observed, updates, steps

    def unpack(self, data):
        (x,y), hp, land, observed, updates, steps = data
        
        move_vector = Point(x,y)
        land =  self.unpack_land(land)
        observed =  self.unpack_observed(observed)
        updates = self.unpack_updates(updates)
        steps = self.unpack_steps(steps)
        
        return move_vector, hp, land, observed, updates, steps

#передвижение
class Move(GameProtocol):
    @staticmethod
    def pack(vector):
        return vector.get()
    
    @staticmethod
    def unpack(message):
        x,y = message
        return [Point(x,y)]

#стрельба
class Strike(GameProtocol):
    @staticmethod
    def pack(vector):
        return vector.get()
    @staticmethod
    def unpack(message):
        x,y = message
        return [Point(x,y)]

#РЕСПАВН
class Respawn(GameProtocol):
    @staticmethod
    def pack(position):
        return position.get()
    @staticmethod
    def unpack(message):
        x,y = message
        return Point(x,y)
#
#словарь хэндлеров на действия
_method_handlers = {'move': Move(),
                'ball': Strike(),
                'look' : Look(),
                'server_accept': ServerAccept(),
                'respawn': Respawn()}
                
                










