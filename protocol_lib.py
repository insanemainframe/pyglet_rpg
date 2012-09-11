#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math_lib import Point

from anyjson import serialize as dumps, deserialize as loads


def pack_server_accept(world_size, position, land, objects):
    land = [point.get()+(tilename,) for point, tilename in land]
    objects = [(object_name, position.get(), tilename) for object_name, (position, tilename) in objects.items()]
    data = (world_size, position.get(), land, objects)
    return dumps(data)

def unpack_server_accept(data):
    if not data:
        return None
    world_size, (x,y), land, objects = loads(data)
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
    return dumps(data)

def f(update):
    if isinstance(update, list):
        return Point(*update)
    else:
        return update


def unpack_server_message(data):
    if not data:
        return None
    (x,y), land, objects, updates = loads(data)
    move_vector = Point(x,y)
    land =  [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name:(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    updates = {name:f(update) for name, update in updates}
    
    return move_vector, land, objects, updates
    
def pack_client_message(vector):
    return dumps(vector.get())

def unpack_client_message(message):
    x,y = loads(message)
    return Point(x,y)


def main():
	
	return 0

if __name__ == '__main__':
	main()

