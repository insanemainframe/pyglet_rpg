#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math_lib import Point
from random import random

from json import dumps, loads as jloads

class ActionError(Exception):
    def __init__(self, action):
        self.error = 'unknown action %s' % action
    def __str__(self):
        return self.error

class JSONError(Exception):
    pass

def loads(data):
    try:
        return jloads(data)
    except Exception, excp:
        raise JSONError(excp.message)

#инициализация
def pack_accept(world_size, position, land, objects):
    pid = hash(random())
    x,y = position.get()
    print 'pack_server_accept %s:%s %s' % (x,y, pid)
    land = [point.get()+(tilename,) for point, tilename in land]
    objects = [(object_name, position.get(), tilename) for object_name, (position, tilename) in objects.items()]
    data = (world_size, (x,y), land, objects, pid)
    return data

def unpack_accept(data):
    world_size, (x,y), land, objects, pid = data
    position = Point(x,y)
    print 'unpack_server_accept %s:%s %s' % (x,y, pid)
    land = [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name :(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    return world_size, position, land, objects

#обзор
def pack_look(move_vector, land, objects, updates):
    move_vector = move_vector.get()
    land = [point.get()+(tilename,) for point, tilename in land]
    new_objects = [(name, position.get(), tile) for name, (position, tile) in objects.items()]
    updates = [(name,update) if update is 'remove' else (name, update.get()) for name, update in updates.items()]
    data = move_vector, land, new_objects, updates
    return data

def unpack_look(data):
    f = lambda update: Point(*update) if isinstance(update, list) else update
    (x,y), land, objects, updates = data
    move_vector = Point(x,y)
    land =  [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name:(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    updates = {name:f(update) for name, update in updates}
    
    return move_vector, land, objects, updates

#передвижение
def pack_client_move(vector):
    return vector.get()

def unpack_client_move(message):
    x,y = message
    return Point(x,y)

#стрельба
def pack_client_ball(vector):
    return vector.get()

def unpack_client_ball(message):
    x,y = message
    return Point(x,y)

#РЕСПАВН
def pack_respawn(position):
    return position.get()

def unpack_respawn(message):
    x,y = message
    return Point(x,y)

def pack(data, action):
    if action=='move_message':
        return dumps((action, pack_client_move(data)))
    elif action=='ball_message':
        return dumps((action, pack_client_ball(data)))
    elif action=='look':
        return dumps((action, pack_look(*data)))
    elif action=='accept':
        return dumps((action, pack_accept(*data)))
    elif action=='respawn':
        return dumps((action, pack_respawn(data)))
    else:
        raise ValueError('unknown action %s' % action )

def unpack(sdata):
    data = loads(sdata)
    action, data = data
    try:
        if action=='move_message':
            return action, unpack_client_move(data)
        elif action=='ball_message':
            return action, unpack_client_ball(data)
        elif action=='look':
            return action, unpack_look(data)
        elif action=='accept':
            return action, unpack_accept(data)
        elif action=='respawn':
            return (action, unpack_respawn(data))
        else:
            raise ActionError(action)
    except JSONError, excp:
        raise excp

if __name__=='__main__':
    pass
