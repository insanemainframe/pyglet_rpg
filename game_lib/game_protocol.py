#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from math_lib import Point
####
class Updates:
    def pack_updates(self, updates):
        result = {}
        for name, action, args in updates:
            if action=='move':
                result[name] = args
                
#инициализация
class ServerAccept(Updates):
    @staticmethod
    def pack(data):
        f = lambda update: update.get() if  isinstance(update, Point)  else update
        world_size, position, land, observed, updates, steps = data
        x,y = position.get()
        land = [point.get()+(tilename,) for point, tilename in land]
        observed = [(i,j) for (i,j) in observed]
        updates = [(name,(position.get(), f(update), tilename))  for name, (position, update, tilename) in updates.items()]
        steps = [(point.get(), step) for point, step in steps]
        data = (world_size, (x,y), land, observed, updates, steps)
        return data

    @staticmethod
    def unpack(data):
        f = lambda update: Point(*update) if isinstance(update, (list,tuple)) else update
        world_size, (x,y), land, observed, updates, steps = data
        position = Point(x,y)
        land = [(Point(x,y),tilename) for x,y, tilename in land]
        observed = [(i,j) for (i,j) in observed]
        updates = {name:(Point(x,y), f(update), tilename) for name, ((x,y),update, tilename) in updates}
        steps = [(Point(x,y), step) for (x,y), step in steps]
        return world_size, position, land, observed, updates, steps

#
#запрос на иницализацию
class ClientAccept:
    @staticmethod
    def pack_client_accept(data):
        name = data
        return name
    
    @staticmethod
    def unpack_client_accept(data):
        name = data
        return name
#обзор
class Look(Updates):
    @staticmethod
    def pack(data):
        f = lambda update: update.get() if  isinstance(update, Point)  else update
        move_vector, land, observed, updates, steps = data
        move_vector = move_vector.get()
        land = [point.get()+(tilename,) for point, tilename in land]
        observed = [(i,j) for (i,j) in observed]
        updates = [(name,(position.get(), f(update), tilename))  for name, (position, update, tilename) in updates.items()]
        steps = [(point.get(), step) for point, step in steps]
        data = move_vector, land, observed, updates, steps
        return data

    @staticmethod
    def unpack(data):
        f = lambda update: Point(*update) if isinstance(update, (list,tuple)) else update
        (x,y), land, observed, updates, steps = data
        move_vector = Point(x,y)
        land =  [(Point(x,y),tilename) for x,y, tilename in land]
        observed = [(i,j) for (i,j) in observed]
        updates = {name:(Point(x,y), f(update), tilename) for name, ((x,y),update, tilename) in updates}
        steps = [(Point(x,y), step) for (x,y), step in steps]
        
        return move_vector, land, observed, updates, steps

#передвижение
class Move:
    @staticmethod
    def pack(vector):
        return vector.get()
    
    @staticmethod
    def unpack(message):
        x,y = message
        return Point(x,y)

#стрельба
class Strike:
    @staticmethod
    def pack(vector):
        return vector.get()
    @staticmethod
    def unpack(message):
        x,y = message
        return Point(x,y)

#РЕСПАВН
class Respawn:
    @staticmethod
    def pack(position):
        return position.get()
    @staticmethod
    def unpack(message):
        x,y = message
        return Point(x,y)
