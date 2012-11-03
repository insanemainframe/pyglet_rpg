#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import SERIALISATION, ZLIB


from zlib import compress as zcompress, decompress as zdecompress

if SERIALISATION=='json':
    from json import loads as marshal_loads, dumps as marshal_dumps
else:
    from marshal import loads as marshal_loads, dumps as marshal_dumps

from share import game_protocol
from share.gameprotocol.meta import GameProtocol



method_handlers = {}

for name in dir(game_protocol):
    Class = getattr(game_protocol, name)
    if type(Class) is type:
        if issubclass(Class, game_protocol.GameProtocol):
            method_handlers[name] = Class

def pack(protocol_object):
    "упаковщик данных"
    assert isinstance(protocol_object, game_protocol.GameProtocol)

    data = protocol_object.pack()

    method = protocol_object.__class__.__name__
    result = dumps((method, data))
    return result

    
def unpack( data):
    "распаковщик"
    try:
        data = loads(data)
    except MarshalError:
        print('MarshalError')
        return None
    else:
        method, data = data
        if method in method_handlers:
            try:
                message = method_handlers[method].unpack(*data)
            except BaseException as excp:
                print('Unpack errror:%s %s %s' % (method, excp, str(data)))
                raise excp
            else:
                return str(method), message
        else:
            print 'Unknown protocol'
            raise MethodError(method,data)



def loads(data):
    try:
        data = decompress(data)
    except BaseException as excp:
        raise ZlibError(excp.message)
    else:
        try:
            return marshal_loads(data)
        except BaseException as excp:
            raise MarshalError(excp.message, data)

def dumps(data):
    try:
        data = marshal_dumps(data)
    except BaseException as excp:
        raise MarshalError(excp.message, data)
    else:
        try:
            return compress(data)
        except BaseException as excp:
            raise ZlibError(excp.message, data)


def compress(data):
    if ZLIB:
        return zcompress(data)
    else:
        return data

def decompress(data):
    if ZLIB:
        return zdecompress(data)
    else:
        return data


class MarshalError(BaseException):
    "шибка распаковки/упаковки marshal"
    def __init__(self, error, data):
        BaseException.__init__(self)
        self.error = error
        self.data = data
    def __str__(self):
        return ' MarshalError %s \n%s' % (self.error, self.data)

class ZlibError(BaseException):
    "ошибка сжатия или распаковки zlib"
    def __init__(self, error, data):
        BaseException.__init__(self)
        self.error = error
        self.data = data
    def __str__(self):
        return ' ZlibError %s \n%s' % (self.error, self.data)


class MethodError(BaseException):
    "неизвестное действие"
    def __init__(self, action, data=''):
        BaseException.__init__(self)
        self.error = 'unknown method %s data \n %s' % (action, data)
    def __str__(self):
        return self.error