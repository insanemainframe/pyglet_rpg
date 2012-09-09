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
    
def pack_server_message(move_vector, land, objects, objects_updates):
    move_vector = move_vector.get()
    land = [point.get()+(tilename,) for point, tilename in land]
    new_objects = [(object_name, position.get(), tilename) for object_name, (position, tilename) in objects.items()]
    objects_updates = [(object_name, vector.get()) for object_name, vector in objects_updates.items()]
    data = move_vector, land, new_objects, objects_updates
    try:
        return dumps(data)
    except:
        print data

def unpack_server_message(data):
    if not data:
        return None
    (x,y), land, objects, objects_updates = loads(data)
    move_vector = Point(x,y)
    land =  [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name:(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    objects_updates = {object_name:Point(x,y) for object_name, (x,y) in objects_updates}
    
    return move_vector, land, objects, objects_updates
    
def pack_client_message(vector):
    return dumps(vector.get())

def unpack_client_message(message):
    x,y = loads(message)
    return Point(x,y)


def main():
	
	return 0

if __name__ == '__main__':
	main()

