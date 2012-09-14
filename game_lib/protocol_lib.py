#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math_lib import Point
from collections import namedtuple

from json import dumps, loads as json_loads

class ActionError(Exception):
    def __init__(self, action):
        self.error = 'unknown action %s' % action
    def __str__(self):
        return self.error

class JSONError(Exception):
    pass

def loads(data):
    try:
        return json_loads(data)
    except Exception, excp:
        raise JSONError(excp.message)

#инициализация
def pack_accept(data):
    print 'pack'
    world_size, position, land, objects, steps = data
    x,y = position.get()
    land = [point.get()+(tilename,) for point, tilename in land]
    objects = [(object_name, position.get(), tilename) for object_name, (position, tilename) in objects.items()]
    steps = [(point.get(), step) for point, step in steps]
    data = (world_size, (x,y), land, objects, steps)
    return data

def unpack_accept(data):
    world_size, (x,y), land, objects, steps = data
    position = Point(x,y)
    land = [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name :(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    steps = [(Point(x,y), step) for (x,y), step in steps]
    return world_size, position, land, objects, steps

#обзор
def pack_look(data):
    move_vector, land, objects, updates, steps = data
    move_vector = move_vector.get()
    land = [point.get()+(tilename,) for point, tilename in land]
    new_objects = [(name, position.get(), tile) for name, (position, tile) in objects.items()]
    updates = [(name,update) if update is 'remove' else (name, update.get()) for name, update in updates.items()]
    steps = [(point.get(), step) for point, step in steps]
    data = move_vector, land, new_objects, updates, steps
    return data

def unpack_look(data):
    f = lambda update: Point(*update) if isinstance(update, list) else update
    (x,y), land, objects, updates, steps = data
    move_vector = Point(x,y)
    land =  [(Point(x,y),tilename) for x,y, tilename in land]
    objects = {object_name:(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    updates = {name:f(update) for name, update in updates}
    steps = [(Point(x,y), step) for (x,y), step in steps]
    
    return move_vector, land, objects, updates, steps

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

#словарь хэндлеров на действия
apair = namedtuple('action_pair',['pack','unpack'])
action_dict = {'move_message': apair(pack_client_move, unpack_client_move),
                'ball_message': apair(pack_client_ball, unpack_client_ball),
                'look' : apair(pack_look, unpack_look),
                'accept': apair(pack_accept, unpack_accept),
                'respawn': apair(pack_respawn, unpack_respawn)}

def pack(data, action):
    "упаковщик данных"
    #print 'pack %s' % action
    if action in action_dict:
        try:
            return dumps((action, action_dict[action][0](data)))
        except Exception, excp:
            print 'PackError %s' % str(data)
            print excp
    else:
        print 'ActionError'
        raise ActionError(action)

def unpack(sdata):
    "распаковщик"
    #print 'unpack'
    data = loads(sdata)
    action, data = data
    if action in action_dict:
        try:
            message = action_dict[action][1](data)
        except:
            print 'unpack errror %s' % message
        else:
            return action, message
    else:
        raise ActionError(action)


