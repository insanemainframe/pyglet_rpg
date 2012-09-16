#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct
from socket import htonl, ntohl, error as socket_error
from marshal import loads as marshal_loads, dumps as marshal_dumps
from zlib import compress, decompress



from math_lib import Point
from collections import namedtuple

#####################################################################
#исключения для ошибок работы протокола

class ActionError(Exception):
    "неизвестное действие"
    def __init__(self, action):
        self.error = 'unknown action %s' % action
    def __str__(self):
        return self.error

class MarshalError:
    "шибка распаковки/упаковки marshal"
    def __init__(self, error, data):
        self.error = error
        self.data = data
    def __str__(self):
        return ' MarshalError %s \n%s' % (self.error, self.data)

class ZlibError:
    "ошибка сжатия или распаковки zlib"
    def __init__(self, error, data):
        self.error = error
        self.data = data
    def __str__(self):
        return ' ZlibError %s \n%s' % (self.error, self.data)

#####################################################################
#упаковка и распаковка пакетов для сокетов
def send(channel, data):
    try:
        value = htonl(len(data))
        size = struct.pack("L",value)
        channel.send(size)
        channel.send(data)
    except socket_error as Error:
        print 'send socket error %s' % Error
    

def receive(channel):
    size = channel.recv(struct.calcsize("L"))
    try:
        size = ntohl(struct.unpack("L", size)[0])
    except struct.error, e:
        print 'struct error %s size %s' % (e,size)
        return ''
    
    data = ""
    while len(data) < size:
        try:
            data+=channel.recv(size - len(data))
        except socket_error as Error:
            errno = Error[0]
            if errno!=11:
                print 'PollServer.send error %s' % Error
                self.handle_error(Error, address)
                return ''
    return data

#####################################################################
#врапперы что бы детектировать ощибки
def loads(data):
    try:
        data = decompress(data)
    except Exception as excp:
        raise ZlibError(excp.message)
    else:
        try:
            return marshal_loads(data)
        except Exception as excp:
            raise MarshalError(excp.message, data)

def dumps(data):
    try:
        data = marshal_dumps(data)
    except Exception as excp:
        raise MarshalError(excp.message)
    else:
        try:
            return compress(data)
        except Exception as excp:
            raise ZlibError(excp.message, data)

#####################################################################
#                                                                   #
#####################################################################
#запрос на иницализацию
def pack_client_accept(data):
    name = data
    return name

def unpack_client_accept(data):
    name = data
    return name
    
#инициализация
def pack_server_accept(data):
    world_size, position, land, observed, objects, steps = data
    x,y = position.get()
    land = [point.get()+(tilename,) for point, tilename in land]
    observed = [(i,j) for (i,j) in observed]
    objects = [(object_name, position.get(), tilename) for object_name, (position, tilename) in objects.items()]
    steps = [(point.get(), step) for point, step in steps]
    data = (world_size, (x,y), land, observed, objects, steps)
    return data

def unpack_server_accept(data):
    world_size, (x,y), land, observed, objects, steps = data
    position = Point(x,y)
    land = [(Point(x,y),tilename) for x,y, tilename in land]
    observed = [(i,j) for (i,j) in observed]
    objects = {object_name :(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    steps = [(Point(x,y), step) for (x,y), step in steps]
    return world_size, position, land, observed, objects, steps


#обзор
def pack_look(data):
    f = lambda update: update.get() if  isinstance(update, Point)  else update
    move_vector, land, observed, objects, updates, steps = data
    move_vector = move_vector.get()
    land = [point.get()+(tilename,) for point, tilename in land]
    observed = [(i,j) for (i,j) in observed]
    new_objects = [(name, position.get(), tile) for name, (position, tile) in objects.items()]
    updates = [(name,(position.get(), f(update), tilename))  for name, (position, update, tilename) in updates.items()]
    steps = [(point.get(), step) for point, step in steps]
    data = move_vector, land, observed, new_objects, updates, steps
    return data

def unpack_look(data):
    f = lambda update: Point(*update) if isinstance(update, (list,tuple)) else update
    (x,y), land, observed, objects, updates, steps = data
    move_vector = Point(x,y)
    land =  [(Point(x,y),tilename) for x,y, tilename in land]
    observed = [(i,j) for (i,j) in observed]
    objects = {object_name:(Point(x,y), tilename) for object_name, (x,y), tilename in objects}
    updates = {name:(Point(x,y), f(update), tilename) for name, ((x,y),update, tilename) in updates}
    steps = [(Point(x,y), step) for (x,y), step in steps]
    
    return move_vector, land, observed, objects, updates, steps

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
                'server_accept': apair(pack_server_accept, unpack_server_accept),
                'respawn': apair(pack_respawn, unpack_respawn)}

def pack(data, action):
    "упаковщик данных"
    if action in action_dict:
        try:
            return dumps((action, action_dict[action][0](data)))
        except Exception as excp:
            print 'PackError: %s %s %s' % (action, excp, str(data))
            raise excp
    else:
        print 'ActionError'
        raise ActionError(action)

def unpack(sdata):
    "распаковщик"
    data = loads(sdata)
    action, data = data
    if action in action_dict:
        try:
            message = action_dict[action][1](data)
        except Exception, excp:
            print 'Unpack errror:%s %s %s' % (action, excp, str(data))
            raise excp
        else:
            return action, message
    else:
        raise ActionError(action)


