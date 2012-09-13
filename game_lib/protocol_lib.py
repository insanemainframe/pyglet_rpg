#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math_lib import Point

from json import dumps, loads


def pack_server_accept(world_size, position, land, objects):
    land = [point.get()+(tilename,) for point, tilename in land]
    objects = [(object_name, position.get(), tilename) for object_name, (position, tilename) in objects.items()]
    data = (world_size, position.get(), land, objects)
    return data

def unpack_server_accept(data):
    world_size, (x,y), land, objects = data
    position = Point(x,y)
    land = [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name :(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    return world_size, position, land, objects
    
def pack_server_message(move_vector, land, objects, updates):
    move_vector = move_vector.get()
    land = [point.get()+(tilename,) for point, tilename in land]
    new_objects = [(name, position.get(), tile) for name, (position, tile) in objects.items()]
    updates = [(name,update) if update is 'remove' else (name, update.get()) for name, update in updates.items()]
    data = move_vector, land, new_objects, updates
    return data


def unpack_server_message(data):
    f = lambda update: Point(*update) if isinstance(update, list) else update
    (x,y), land, objects, updates = data
    move_vector = Point(x,y)
    land =  [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name:(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    updates = {name:f(update) for name, update in updates}
    
    return move_vector, land, objects, updates
    
def pack_client_move(vector):
    return vector.get()

def unpack_client_move(message):
    x,y = message
    return Point(x,y)

def pack_client_ball(vector):
    return vector.get()

def unpack_client_ball(message):
    x,y = message
    return Point(x,y)


def pack(data, action):
    if action=='move_message':
        return dumps((action, pack_client_move(data)))
    elif action=='ball_message':
        return dumps((action, pack_client_ball(data)))
    elif action=='server_message':
        return dumps((action, pack_server_message(*data)))
    elif action=='accept':
        return dumps((action, pack_server_accept(*data)))
    else:
        print action, data
        raise ValueError('unknown action %s' % action )

def unpack(sdata):
    data = loads(sdata)
    action, data = data
    if action=='move_message':
        return action, unpack_client_move(data)
    elif action=='ball_message':
        return action, unpack_client_ball(data)
    elif action=='server_message':
        return action, unpack_server_message(data)
    elif action=='accept':
        return action, unpack_server_accept(data)
    else:
        print sdata
        raise ValueError('unknown action %s' % action )

if __name__=='_main__':
    pass
